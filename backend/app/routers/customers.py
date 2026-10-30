from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_company_scoped_or_404, record_audit
from app.models import Customer, Room, Site, User, UserRole
from app.schemas import (
    CustomerCreate,
    CustomerOut,
    RoomCreate,
    RoomOut,
    SiteCreate,
    SiteOut,
)
from app.security import get_current_user, require_role

router = APIRouter(tags=["customers"])


@router.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor)),
):
    customer = Customer(company_id=current_user.company_id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    record_audit(db, current_user.company_id, current_user.id, "create", "customer", customer.id)
    return customer


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Customer).filter(Customer.company_id == current_user.company_id).all()


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_company_scoped_or_404(db, Customer, customer_id, current_user.company_id)


@router.post("/sites", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
def create_site(
    payload: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor)),
):
    get_company_scoped_or_404(db, Customer, payload.customer_id, current_user.company_id)
    site = Site(company_id=current_user.company_id, **payload.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    record_audit(db, current_user.company_id, current_user.id, "create", "site", site.id)
    return site


@router.get("/sites", response_model=list[SiteOut])
def list_sites(
    customer_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Site).filter(Site.company_id == current_user.company_id)
    if customer_id:
        query = query.filter(Site.customer_id == customer_id)
    return query.all()


@router.get("/sites/{site_id}", response_model=SiteOut)
def get_site(site_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_company_scoped_or_404(db, Site, site_id, current_user.company_id)


@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor)),
):
    get_company_scoped_or_404(db, Site, payload.site_id, current_user.company_id)
    room = Room(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(site_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_company_scoped_or_404(db, Site, site_id, current_user.company_id)
    return db.query(Room).filter(Room.site_id == site_id).all()
