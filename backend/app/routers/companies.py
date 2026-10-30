from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import PLAN_LIMITS
from app.database import get_db
from app.models import User, UserRole
from app.schemas import CompanyOut
from app.security import require_role

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/me", response_model=CompanyOut)
def get_my_company(db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.viewer))):
    return current_user.company


@router.get("/me/usage")
def get_my_usage(current_user: User = Depends(require_role(UserRole.supervisor))):
    """Mock billing/usage foundation (spec section 13/15): reports AI usage
    against the plan's monthly allowance. No real payment processing."""
    plan = current_user.company.subscription_plan.value
    limits = PLAN_LIMITS[plan]
    used = current_user.company.ai_requests_used_this_month
    limit = limits["ai_requests_per_month"]
    return {
        "plan": plan,
        "ai_requests_used_this_month": used,
        "ai_requests_limit": limit,
        "ai_requests_remaining": None if limit is None else max(limit - used, 0),
        "over_limit": False if limit is None else used >= limit,
    }
