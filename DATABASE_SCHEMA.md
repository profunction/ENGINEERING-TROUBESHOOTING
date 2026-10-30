# Database Schema

Reflects `backend/app/models.py` exactly (Phase 1 implementation). All
tables except `rooms` (child of `sites`, which is already company-scoped)
carry a `company_id` for tenant isolation.

## Entity-relationship summary

```
Company 1───* User
Company 1───* Customer 1───* Site 1───* Room
                               Site 1───* Equipment
Company 1───* WorkOrder ──* ServiceNote
                          ──* Photo
                          ──1 ServiceReport
Equipment 1───* MaintenanceRecord (optionally linked to a WorkOrder)
Company 1───* AuditLog
```

## Tables

### companies
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| name | string | |
| industry | string | free text, e.g. `av_vc`, `hvac`, `elevator` — not an enum, so new industries need no migration |
| subscription_plan | enum(starter/pro/enterprise) | |
| ai_requests_used_this_month | int | mock usage counter, see COMMERCIAL_PLANS.md |
| created_at | datetime | |

### users
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | |
| email | string, indexed | |
| hashed_password | string | bcrypt via passlib |
| full_name | string | |
| role | enum(owner/admin/supervisor/engineer/viewer) | |
| is_active | bool | |
| created_at | datetime | |

### customers
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | |
| name | string | |
| contact_name / contact_email / contact_phone | string, nullable | |
| address | text, nullable | |
| created_at | datetime | |

### sites
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | denormalized for fast tenant filtering without a join |
| customer_id | FK → customers | |
| name | string | |
| address | text, nullable | |

### rooms
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| site_id | FK → sites | location/room record under a site |
| name | string | |

### equipment
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | |
| site_id | FK → sites | |
| room_id | FK → rooms, nullable | |
| manufacturer / model | string | |
| serial_number | string, nullable | |
| category | string, nullable | e.g. `codec`, `chiller`, `elevator_controller` |
| installation_date | datetime, nullable | |
| firmware_version | string, nullable | |
| notes | text, nullable | |

### work_orders
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | |
| customer_id | FK → customers | |
| site_id | FK → sites | |
| equipment_id | FK → equipment, nullable | |
| title / description | string / text | |
| status | enum: open, assigned, in_progress, waiting_for_parts, pending_customer, completed, closed | |
| priority | enum: low, normal, high, urgent | |
| assigned_engineer_id | FK → users, nullable | |
| created_by_id | FK → users | |
| arrival_time / work_start_time / work_end_time | datetime, nullable | |
| customer_acknowledged | bool | |
| created_at / updated_at / closed_at | datetime | `closed_at` set automatically when status → closed |

Closed work orders are immutable (enforced in `routers/work_orders.py`,
not just at the schema level).

### service_notes
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| work_order_id | FK → work_orders | |
| author_id | FK → users | |
| note_type | enum: initial_condition, investigation, outcome, follow_up, general | |
| content | text | |
| created_at | datetime | |

### photos
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| work_order_id | FK → work_orders | |
| file_path | string | local disk in Phase 1; swaps to an S3 key later |
| caption | string, nullable | |
| uploaded_by_id | FK → users | |

Not yet exposed via an API endpoint — the table and relation exist; upload
handling is Phase 2 work.

### maintenance_records
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| equipment_id | FK → equipment | |
| work_order_id | FK → work_orders, nullable | kept optional so legacy/manually-logged history can be recorded without a formal work order |
| event_date | datetime | |
| description | text | |
| engineer_id | FK → users, nullable | |
| firmware_version | string, nullable | |
| parts_replaced | text, nullable | |

### service_reports
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| work_order_id | FK → work_orders, unique | one report per work order |
| initial_condition / investigation / outcome / follow_up / parts_used | text, nullable | blank → rendered as "[REQUIRES ENGINEER CONFIRMATION]" at export time, never fabricated |
| engineer_signature_name / customer_signature_name | string, nullable | text-only in Phase 1; real signature capture is Phase 5 |
| pdf_path / docx_path | string, nullable | |
| generated_by_id | FK → users | |
| generated_at | datetime | |

### audit_logs
| column | type | notes |
|---|---|---|
| id | string(32) PK | |
| company_id | FK → companies | |
| user_id | FK → users, nullable | |
| action | string | e.g. `create`, `update`, `generate` |
| entity_type | string | e.g. `work_order`, `service_report` |
| entity_id | string, nullable | |
| timestamp | datetime | |

## Design notes

- **IDs are UUID4 hex strings**, not auto-increment integers, so IDs never
  leak row counts and are safe to generate client-side offline (needed for
  the mobile app's offline "create while disconnected" flow) without a
  server round-trip or collision risk.
- **No cross-company foreign key exists anywhere.** This is a structural
  guarantee, not just an application-layer check.
