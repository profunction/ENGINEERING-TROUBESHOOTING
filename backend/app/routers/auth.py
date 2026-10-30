from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, User, UserRole
from app.schemas import CompanySignup, LoginRequest, Token, UserCreate, UserOut
from app.security import create_access_token, get_current_user, hash_password, require_role, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: CompanySignup, db: Session = Depends(get_db)):
    """Creates a new company tenant with its first user as 'owner'."""
    existing = db.query(User).filter(User.email == payload.owner_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    company = Company(name=payload.company_name, industry=payload.industry)
    db.add(company)
    db.flush()

    owner = User(
        company_id=company.id,
        email=payload.owner_email,
        hashed_password=hash_password(payload.owner_password),
        full_name=payload.owner_full_name,
        role=UserRole.owner,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    token = create_access_token(owner.id, company.id)
    return Token(access_token=token, user=UserOut.model_validate(owner))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
    token = create_access_token(user.id, user.company_id)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """Admins and owners can provision engineers/supervisors/viewers within their own company."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        company_id=current_user.company_id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.supervisor)),
):
    return db.query(User).filter(User.company_id == current_user.company_id).all()
