from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import (
    ServiceNoteType,
    SubscriptionPlan,
    UserRole,
    WorkOrderPriority,
    WorkOrderStatus,
)


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Auth / Company / User ----


class CompanySignup(BaseModel):
    company_name: str
    industry: Optional[str] = None
    owner_email: EmailStr
    owner_password: str
    owner_full_name: str


class CompanyOut(ORMBase):
    id: str
    name: str
    industry: Optional[str]
    subscription_plan: SubscriptionPlan
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.engineer


class UserOut(ORMBase):
    id: str
    company_id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---- Customer / Site / Room ----


class CustomerCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class CustomerOut(ORMBase):
    id: str
    company_id: str
    name: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    created_at: datetime


class SiteCreate(BaseModel):
    customer_id: str
    name: str
    address: Optional[str] = None


class SiteOut(ORMBase):
    id: str
    company_id: str
    customer_id: str
    name: str
    address: Optional[str]
    created_at: datetime


class RoomCreate(BaseModel):
    site_id: str
    name: str


class RoomOut(ORMBase):
    id: str
    site_id: str
    name: str


# ---- Equipment ----


class EquipmentCreate(BaseModel):
    site_id: str
    room_id: Optional[str] = None
    manufacturer: str
    model: str
    serial_number: Optional[str] = None
    category: Optional[str] = None
    installation_date: Optional[datetime] = None
    firmware_version: Optional[str] = None
    notes: Optional[str] = None


class EquipmentOut(ORMBase):
    id: str
    company_id: str
    site_id: str
    room_id: Optional[str]
    manufacturer: str
    model: str
    serial_number: Optional[str]
    category: Optional[str]
    installation_date: Optional[datetime]
    firmware_version: Optional[str]
    notes: Optional[str]
    created_at: datetime


class MaintenanceRecordCreate(BaseModel):
    work_order_id: Optional[str] = None
    description: str
    firmware_version: Optional[str] = None
    parts_replaced: Optional[str] = None
    event_date: Optional[datetime] = None


class MaintenanceRecordOut(ORMBase):
    id: str
    equipment_id: str
    work_order_id: Optional[str]
    event_date: datetime
    description: str
    engineer_id: Optional[str]
    firmware_version: Optional[str]
    parts_replaced: Optional[str]


class EquipmentHistorySummary(BaseModel):
    """Separates observed facts (records) from an AI-style rollup. The
    'analysis' block is deterministic (no AI call) for the MVP: counts and
    repeated-fault detection only. See AI_RAG_DESIGN.md for the planned
    Phase 4 AI summarization layer."""

    equipment: EquipmentOut
    records: list[MaintenanceRecordOut]
    total_incidents: int
    repeated_descriptions: list[str]
    note: str = "Deterministic summary of logged records only; no AI-generated hypotheses included."


# ---- Work Orders ----


class WorkOrderCreate(BaseModel):
    customer_id: str
    site_id: str
    equipment_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: WorkOrderPriority = WorkOrderPriority.normal
    assigned_engineer_id: Optional[str] = None


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkOrderStatus] = None
    priority: Optional[WorkOrderPriority] = None
    assigned_engineer_id: Optional[str] = None
    arrival_time: Optional[datetime] = None
    work_start_time: Optional[datetime] = None
    work_end_time: Optional[datetime] = None
    customer_acknowledged: Optional[bool] = None


class WorkOrderOut(ORMBase):
    id: str
    company_id: str
    customer_id: str
    site_id: str
    equipment_id: Optional[str]
    title: str
    description: Optional[str]
    status: WorkOrderStatus
    priority: WorkOrderPriority
    assigned_engineer_id: Optional[str]
    created_by_id: str
    arrival_time: Optional[datetime]
    work_start_time: Optional[datetime]
    work_end_time: Optional[datetime]
    customer_acknowledged: bool
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]


# ---- Service Notes ----


class ServiceNoteCreate(BaseModel):
    note_type: ServiceNoteType = ServiceNoteType.general
    content: str


class ServiceNoteOut(ORMBase):
    id: str
    work_order_id: str
    author_id: str
    note_type: ServiceNoteType
    content: str
    created_at: datetime


# ---- Service Reports ----


class ServiceReportCreate(BaseModel):
    initial_condition: Optional[str] = None
    investigation: Optional[str] = None
    outcome: Optional[str] = None
    follow_up: Optional[str] = None
    parts_used: Optional[str] = None
    engineer_signature_name: Optional[str] = None
    customer_signature_name: Optional[str] = None


class ServiceReportOut(ORMBase):
    id: str
    work_order_id: str
    initial_condition: Optional[str]
    investigation: Optional[str]
    outcome: Optional[str]
    follow_up: Optional[str]
    parts_used: Optional[str]
    engineer_signature_name: Optional[str]
    customer_signature_name: Optional[str]
    pdf_path: Optional[str]
    docx_path: Optional[str]
    generated_by_id: str
    generated_at: datetime
