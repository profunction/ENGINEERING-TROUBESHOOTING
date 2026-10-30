from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_company_scoped_or_404, record_audit
from app.models import Customer, Equipment, Site, User, UserRole, WorkOrder, WorkOrderStatus
from app.schemas import ServiceNoteCreate, ServiceNoteOut, WorkOrderCreate, WorkOrderOut, WorkOrderUpdate
from app.security import get_current_user, require_role

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

# Statuses from which a work order may still move forward; "closed" is terminal.
TERMINAL_STATUSES = {WorkOrderStatus.closed}


@router.post("", response_model=WorkOrderOut, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.engineer)),
):
    get_company_scoped_or_404(db, Customer, payload.customer_id, current_user.company_id)
    get_company_scoped_or_404(db, Site, payload.site_id, current_user.company_id)
    if payload.equipment_id:
        get_company_scoped_or_404(db, Equipment, payload.equipment_id, current_user.company_id)

    data = payload.model_dump()
    status_value = WorkOrderStatus.assigned if data.get("assigned_engineer_id") else WorkOrderStatus.open
    work_order = WorkOrder(
        company_id=current_user.company_id,
        created_by_id=current_user.id,
        status=status_value,
        **data,
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    record_audit(db, current_user.company_id, current_user.id, "create", "work_order", work_order.id)
    return work_order


@router.get("", response_model=list[WorkOrderOut])
def list_work_orders(
    status_filter: WorkOrderStatus | None = None,
    assigned_engineer_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(WorkOrder).filter(WorkOrder.company_id == current_user.company_id)
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    if assigned_engineer_id:
        query = query.filter(WorkOrder.assigned_engineer_id == assigned_engineer_id)
    return query.order_by(WorkOrder.created_at.desc()).all()


@router.get("/{work_order_id}", response_model=WorkOrderOut)
def get_work_order(
    work_order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)


@router.patch("/{work_order_id}", response_model=WorkOrderOut)
def update_work_order(
    work_order_id: str,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.engineer)),
):
    work_order = get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    if work_order.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=400, detail="Work order is closed and cannot be modified")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(work_order, field, value)

    if updates.get("status") == WorkOrderStatus.closed:
        from datetime import datetime

        work_order.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(work_order)
    record_audit(db, current_user.company_id, current_user.id, "update", "work_order", work_order.id)
    return work_order


@router.post(
    "/{work_order_id}/notes", response_model=ServiceNoteOut, status_code=status.HTTP_201_CREATED
)
def add_service_note(
    work_order_id: str,
    payload: ServiceNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import ServiceNote

    work_order = get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    note = ServiceNote(work_order_id=work_order.id, author_id=current_user.id, **payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{work_order_id}/notes", response_model=list[ServiceNoteOut])
def list_service_notes(
    work_order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    from app.models import ServiceNote

    get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    return (
        db.query(ServiceNote)
        .filter(ServiceNote.work_order_id == work_order_id)
        .order_by(ServiceNote.created_at.asc())
        .all()
    )
