import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class UserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    supervisor = "supervisor"
    engineer = "engineer"
    viewer = "viewer"


class WorkOrderStatus(str, enum.Enum):
    open = "open"
    assigned = "assigned"
    in_progress = "in_progress"
    waiting_for_parts = "waiting_for_parts"
    pending_customer = "pending_customer"
    completed = "completed"
    closed = "closed"


class WorkOrderPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class ServiceNoteType(str, enum.Enum):
    initial_condition = "initial_condition"
    investigation = "investigation"
    outcome = "outcome"
    follow_up = "follow_up"
    general = "general"


class SubscriptionPlan(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"


class Company(Base):
    """A tenant. All other business data is scoped to a company_id for isolation."""

    __tablename__ = "companies"

    id = Column(String(32), primary_key=True, default=gen_id)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)  # e.g. "av_vc", "hvac", "elevator"
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.starter)
    ai_requests_used_this_month = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.engineer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="users")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="customers")
    sites = relationship("Site", back_populates="customer", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "sites"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sites")
    rooms = relationship("Room", back_populates="site", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="site", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(String(32), primary_key=True, default=gen_id)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False)
    name = Column(String(255), nullable=False)

    site = relationship("Site", back_populates="rooms")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False)
    room_id = Column(String(32), ForeignKey("rooms.id"), nullable=True)
    manufacturer = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    serial_number = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)  # e.g. "codec", "chiller", "elevator_controller"
    installation_date = Column(DateTime, nullable=True)
    firmware_version = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="equipment")
    work_orders = relationship("WorkOrder", back_populates="equipment")
    maintenance_records = relationship(
        "MaintenanceRecord", back_populates="equipment", cascade="all, delete-orphan"
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False)
    equipment_id = Column(String(32), ForeignKey("equipment.id"), nullable=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.open)
    priority = Column(Enum(WorkOrderPriority), default=WorkOrderPriority.normal)

    assigned_engineer_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    created_by_id = Column(String(32), ForeignKey("users.id"), nullable=False)

    arrival_time = Column(DateTime, nullable=True)
    work_start_time = Column(DateTime, nullable=True)
    work_end_time = Column(DateTime, nullable=True)
    customer_acknowledged = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    equipment = relationship("Equipment", back_populates="work_orders")
    service_notes = relationship(
        "ServiceNote", back_populates="work_order", cascade="all, delete-orphan"
    )
    photos = relationship("Photo", back_populates="work_order", cascade="all, delete-orphan")
    report = relationship(
        "ServiceReport", back_populates="work_order", uselist=False, cascade="all, delete-orphan"
    )


class ServiceNote(Base):
    __tablename__ = "service_notes"

    id = Column(String(32), primary_key=True, default=gen_id)
    work_order_id = Column(String(32), ForeignKey("work_orders.id"), nullable=False)
    author_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    note_type = Column(Enum(ServiceNoteType), default=ServiceNoteType.general)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="service_notes")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(String(32), primary_key=True, default=gen_id)
    work_order_id = Column(String(32), ForeignKey("work_orders.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    caption = Column(String(255), nullable=True)
    uploaded_by_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="photos")


class MaintenanceRecord(Base):
    """Historical maintenance/fault entry for an equipment item, independent of
    whether it came from a formal work order (keeps equipment history queryable
    even for legacy/manually-logged events)."""

    __tablename__ = "maintenance_records"

    id = Column(String(32), primary_key=True, default=gen_id)
    equipment_id = Column(String(32), ForeignKey("equipment.id"), nullable=False)
    work_order_id = Column(String(32), ForeignKey("work_orders.id"), nullable=True)
    event_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=False)
    engineer_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    firmware_version = Column(String(100), nullable=True)
    parts_replaced = Column(Text, nullable=True)

    equipment = relationship("Equipment", back_populates="maintenance_records")


class ServiceReport(Base):
    __tablename__ = "service_reports"

    id = Column(String(32), primary_key=True, default=gen_id)
    work_order_id = Column(String(32), ForeignKey("work_orders.id"), nullable=False, unique=True)

    initial_condition = Column(Text, nullable=True)
    investigation = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    follow_up = Column(Text, nullable=True)
    parts_used = Column(Text, nullable=True)

    engineer_signature_name = Column(String(255), nullable=True)
    customer_signature_name = Column(String(255), nullable=True)

    pdf_path = Column(String(500), nullable=True)
    docx_path = Column(String(500), nullable=True)

    generated_by_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(32), primary_key=True, default=gen_id)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(32), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
