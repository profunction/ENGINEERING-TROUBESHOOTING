from collections import Counter

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_company_scoped_or_404, record_audit
from app.models import Equipment, MaintenanceRecord, Site, User, UserRole
from app.schemas import (
    EquipmentCreate,
    EquipmentHistorySummary,
    EquipmentOut,
    MaintenanceRecordCreate,
    MaintenanceRecordOut,
)
from app.security import get_current_user, require_role

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor)),
):
    get_company_scoped_or_404(db, Site, payload.site_id, current_user.company_id)
    item = Equipment(company_id=current_user.company_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    record_audit(db, current_user.company_id, current_user.id, "create", "equipment", item.id)
    return item


@router.get("", response_model=list[EquipmentOut])
def list_equipment(
    site_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Equipment).filter(Equipment.company_id == current_user.company_id)
    if site_id:
        query = query.filter(Equipment.site_id == site_id)
    return query.all()


@router.get("/{equipment_id}", response_model=EquipmentOut)
def get_equipment(
    equipment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_company_scoped_or_404(db, Equipment, equipment_id, current_user.company_id)


@router.post(
    "/{equipment_id}/maintenance-records",
    response_model=MaintenanceRecordOut,
    status_code=status.HTTP_201_CREATED,
)
def add_maintenance_record(
    equipment_id: str,
    payload: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_company_scoped_or_404(db, Equipment, equipment_id, current_user.company_id)
    data = payload.model_dump()
    record = MaintenanceRecord(equipment_id=equipment_id, engineer_id=current_user.id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{equipment_id}/history", response_model=EquipmentHistorySummary)
def get_equipment_history(
    equipment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the equipment's maintenance history plus a deterministic
    (non-AI) summary: total incidents and any description repeated 2+ times,
    which is a simple proxy for a recurring fault. This supports queries like
    'what problems has this unit had recently?' without an AI call. Future
    Phase 4 work may layer an LLM-generated narrative on top, clearly
    labelled as a hypothesis - see AI_RAG_DESIGN.md."""
    equipment = get_company_scoped_or_404(db, Equipment, equipment_id, current_user.company_id)
    records = (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.equipment_id == equipment_id)
        .order_by(MaintenanceRecord.event_date.desc())
        .all()
    )
    counts = Counter(r.description.strip().lower() for r in records)
    repeated = [desc for desc, n in counts.items() if n >= 2]
    return EquipmentHistorySummary(
        equipment=equipment,
        records=records,
        total_incidents=len(records),
        repeated_descriptions=repeated,
    )
