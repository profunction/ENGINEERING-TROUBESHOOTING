from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_company_scoped_or_404, record_audit
from app.models import Customer, Equipment, ServiceReport, Site, User, WorkOrder
from app.schemas import ServiceReportCreate, ServiceReportOut
from app.security import get_current_user
from app.services.report_generator import generate_docx, generate_pdf

router = APIRouter(prefix="/work-orders/{work_order_id}/report", tags=["reports"])


@router.post("", response_model=ServiceReportOut, status_code=status.HTTP_201_CREATED)
def create_or_update_report(
    work_order_id: str,
    payload: ServiceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    work_order = get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)

    report = db.query(ServiceReport).filter(ServiceReport.work_order_id == work_order_id).first()
    data = payload.model_dump()
    if report:
        for field, value in data.items():
            setattr(report, field, value)
    else:
        report = ServiceReport(work_order_id=work_order_id, generated_by_id=current_user.id, **data)
        db.add(report)
    db.commit()
    db.refresh(report)

    customer = db.query(Customer).filter(Customer.id == work_order.customer_id).first()
    site = db.query(Site).filter(Site.id == work_order.site_id).first()
    equipment = (
        db.query(Equipment).filter(Equipment.id == work_order.equipment_id).first()
        if work_order.equipment_id
        else None
    )
    engineer = work_order.assigned_engineer_id and db.query(User).filter(
        User.id == work_order.assigned_engineer_id
    ).first()

    report.pdf_path = generate_pdf(work_order, report, customer, site, equipment, engineer)
    report.docx_path = generate_docx(work_order, report, customer, site, equipment, engineer)
    db.commit()
    db.refresh(report)

    record_audit(db, current_user.company_id, current_user.id, "generate", "service_report", report.id)
    return report


@router.get("", response_model=ServiceReportOut)
def get_report(
    work_order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    report = db.query(ServiceReport).filter(ServiceReport.work_order_id == work_order_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return report


@router.get("/pdf")
def download_pdf(
    work_order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    report = db.query(ServiceReport).filter(ServiceReport.work_order_id == work_order_id).first()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated yet")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"{work_order_id}.pdf")


@router.get("/docx")
def download_docx(
    work_order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    get_company_scoped_or_404(db, WorkOrder, work_order_id, current_user.company_id)
    report = db.query(ServiceReport).filter(ServiceReport.work_order_id == work_order_id).first()
    if not report or not report.docx_path:
        raise HTTPException(status_code=404, detail="DOCX not generated yet")
    return FileResponse(
        report.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{work_order_id}.docx",
    )
