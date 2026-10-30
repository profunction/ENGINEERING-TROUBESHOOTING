import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./fieldops.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
JWT_ALGORITHM = "HS256"

# Free/default usage limits per subscription plan, used by the mock billing
# foundation (section 15/13 of the spec). Not wired to real payments.
PLAN_LIMITS = {
    "starter": {"ai_requests_per_month": 200, "stored_reports": 500, "storage_mb": 2048},
    "pro": {"ai_requests_per_month": 2000, "stored_reports": 5000, "storage_mb": 20480},
    "enterprise": {"ai_requests_per_month": None, "stored_reports": None, "storage_mb": None},
}

FILE_STORAGE_DIR = os.environ.get("FILE_STORAGE_DIR", "./storage")
REPORTS_DIR = os.path.join(FILE_STORAGE_DIR, "reports")
PHOTOS_DIR = os.path.join(FILE_STORAGE_DIR, "photos")
