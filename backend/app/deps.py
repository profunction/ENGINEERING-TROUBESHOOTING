from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AuditLog


def get_company_scoped_or_404(db: Session, model, obj_id: str, company_id: str):
    """Fetch a row by id, scoped to company_id. Returns 404 (not 403) for a
    row that belongs to another company, so tenants can't probe for the
    existence of another company's records."""
    obj = db.query(model).filter(model.id == obj_id, model.company_id == company_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj


def record_audit(db: Session, company_id: str, user_id: str, action: str, entity_type: str, entity_id: str):
    db.add(
        AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    )
    db.commit()
