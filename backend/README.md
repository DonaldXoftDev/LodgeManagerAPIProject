# LodgeOps — Lodge Management API

**A modern, enterprise-grade property management backend** built with FastAPI.

LodgeOps is a production-quality REST API that handles everything a residential lodge or student accommodation needs: tenant onboarding (via a secure invite system), room lifecycle management, lease contracts, rent payment tracking, and real-time financial dashboard analytics.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture-the-n-tier-pattern)
- [Domain Model](#-domain-model)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)

---

## 🚀 Features

### Core Business Modules
- **Authentication & Authorization:** Stateless JWT-based auth with rotating Refresh Tokens stored as HTTP-only cookies. Role-based access control (Landlord & Tenant) enforced at the dependency injection layer on every endpoint.
- **Invite-Only Tenant Registration:** Tenants cannot self-register. Landlords generate time-limited UUID invite links scoped to a specific lodge. Tenants submit requests and are held in a `PENDING` state until the Landlord approves them.
- **Lodge & Room Management:** Landlords can create lodges and bulk-generate rooms using a `RoomGenerator` payload (prefix, range, default rent). Room status is tracked across three states: `Vacant`, `Occupied`, and `Maintenance`.
- **Lease Lifecycle Management:** Full contract lifecycle from creation to termination. Lease status (`Active`, `Overdue`, `Pending_Termination`, `Terminated`) is **never stored** in the database — it is computed dynamically via a Python `@property` on the model to prevent stale states.
- **Append-Only Payment Ledger:** Every rent collection creates a new payment record. Records are never edited. Outstanding balances and revenue metrics are computed at query time using SQL aggregations.

### Advanced Dashboard & Analytics
- **Landlord Dashboard:** Real-time lodge overview including financial performance and a room intelligence grid categorising every room as Safe, Expiring, Overdue, Owing, Vacant, or Maintenance.
- **Financial Aggregations:** `func.sum` and `outerjoin` compute Potential Revenue, Expected Revenue, Collected Revenue, and Unpaid Rent directly in the database. No Python loops over ORM objects.
- **Tenant Dashboard:** Personal lease status, payment history, and outstanding balance for the authenticated tenant.

### Technical Highlights
- **Clean N-Tier Architecture:** Hard separation between Presentation (`api/`), Business Logic (`services/`), Data Access (`crud/`), Domain Models (`models/`), and Data Contracts (`schemas/`).
- **Pydantic v2 Strict Contracts:** `Create`, `Update`, and `Response` schemas are always separate objects per domain. `LeaseUpdate` is intentionally restricted to `end_date` and `agreed_rent_amt` only — `tenant_id`, `room_id`, and `start_date` cannot be mutated post-creation.
- **Alembic Migrations:** All schema changes go through versioned Alembic migrations. `Base.metadata.create_all()` is not used in any production flow.
- **Comprehensive Test Suite:** 150+ tests with an isolated in-memory SQLite test database. 96%+ code coverage across all layers.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Python 3.11+, FastAPI |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | PyJWT, Passlib + Bcrypt 4.0.1, HTTP-only Cookie sessions |
| **Database** | SQLite (Development) / PostgreSQL-ready (Production) |
| **Testing** | Pytest, pytest-cov, HTTPX |

---

## 🏗 Architecture: The N-Tier Pattern

Every feature request passes strictly through the following layers. No layer skips another.

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────────────────┐
│         Presentation Layer  (app/api/v1/)        │
│  FastAPI Routers + Dependency Injection          │
│  [No SQL. No Business Logic.]                    │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│      Business Logic Layer  (app/services/)       │
│  Orchestrates workflows, enforces domain rules   │
│  [No HTTP objects. No raw SQL.]                  │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│       Data Access Layer  (app/crud/)             │
│  Raw SQLAlchemy queries + aggregations           │
│  [No business logic.]                            │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌────────────────────────────┐  ┌─────────────────────────────┐
│  Domain Models (app/models/)│  │  Data Contracts (app/schemas/)│
│  SQLAlchemy ORM + @property │  │  Pydantic Create/Update/     │
│  + Cascade rules            │  │  Response per domain         │
└────────────────────────────┘  └─────────────────────────────┘
                    │
                    ▼
              Database (SQLite / PostgreSQL)
```

---

## 🗄 Domain Model

The system is built on 8 core entities:

| Entity | Table | Purpose |
|---|---|---|
| **User** | `users` | Core identity for both Landlords and Tenants. Holds email, hashed password, and role. |
| **RefreshToken** | `refresh_tokens` | Tracks active refresh tokens per user for secure token rotation and logout. |
| **Invite** | `invitations` | UUID-based invite links generated by Landlords, scoped to a Lodge with an expiry. |
| **Lodge** | `lodges` | A physical property owned by a Landlord. Parent of all Rooms and TenantProfiles. |
| **Room** | `rooms` | An individual rentable unit within a Lodge. Tracks status and base rent price. |
| **TenantProfile** | `tenant_profiles` | Extended profile for Tenant users — Student Level, department, emergency contacts. |
| **Lease** | `leases` | The contract linking a Tenant to a Room. Status computed dynamically, never stored stale. |
| **Payment** | `payments` | Append-only ledger of every rent collection. Balances computed via SQL aggregation. |

**Key Cascade Rule:** Deleting a `Lodge` cascades to all its `Rooms`, `TenantProfiles`, and `Invites` via `ondelete='CASCADE'` at the DB level and `cascade='all, delete-orphan'` at the ORM level.

---

## 📡 API Reference

All routes are prefixed with `/api/v1`. Interactive documentation is available at `/docs` once the server is running.

### Authentication — `/api/v1/auth`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/register/landlord` | Public | Register a new Landlord account |
| `POST` | `/register/tenant` | Public (requires Invite UUID) | Register a new Tenant via invite link |
| `POST` | `/login` | Public | Authenticate and receive tokens as HTTP-only cookies |
| `POST` | `/refresh` | Authenticated | Rotate access token using refresh cookie |
| `GET` | `/me` | Authenticated | Get the currently authenticated user's profile |
| `POST` | `/logout` | Authenticated | Invalidate refresh token and clear session cookies |

### Lodges — `/api/v1/lodges`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/register` | Landlord | Create a new lodge (with optional bulk room generation) |
| `GET` | `/` | Landlord | Get all lodges owned by the authenticated landlord |
| `GET` | `/{lodge_id}` | Landlord | Get a specific lodge by ID |
| `PATCH` | `/{lodge_id}` | Landlord | Update lodge name or address |
| `GET` | `/{lodge_id}/tenants` | Landlord | List all tenants in a lodge |
| `PATCH` | `/{lodge_id}/rooms/bulk-update` | Landlord | Bulk update base rent for selected rooms |

### Rooms — `/api/v1/rooms`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/` | Landlord | Add a new room to a lodge |
| `GET` | `/{lodge_id}/rooms` | Landlord | Get all rooms in a lodge |
| `PATCH` | `/{room_id}` | Landlord | Update room details or status |

### Tenants — `/api/v1/tenants`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/profile` | Tenant | Get the authenticated tenant's own profile |
| `PATCH` | `/profiles/me` | Tenant | Update the authenticated tenant's own profile |
| `PATCH` | `/{tenant_id}/status` | Landlord | Approve or reject a pending tenant |

### Leases — `/api/v1/leases`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/` | Landlord | Create a new lease (room must be vacant, tenant must be in same lodge) |
| `GET` | `/{lodge_id}` | Landlord | Get all leases in a lodge with optional filters |
| `GET` | `/me` | Tenant | Get the authenticated tenant's own lease history |
| `PATCH` | `/{lease_id}` | Landlord | Amend `end_date` or `agreed_rent_amt` only |
| `PATCH` | `/terminate/{lease_id}` | Landlord | Terminate an active lease |
| `PATCH` | `/appeal/{lease_id}` | Tenant | Submit a termination appeal for own lease |
| `GET` | `/{lodge_id}/occupied-rooms` | Landlord | Get all occupied rooms categorised by health status |

### Payments — `/api/v1/payments`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/create-payment` | Landlord | Record a rent payment against a lease |
| `GET` | `/{lease_id}` | Landlord | Get payment history for a specific lease |
| `GET` | `/me/{lease_id}` | Tenant | Get own payment history for a specific lease |

### Invites — `/api/v1/invites`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/` | Landlord | Generate a new invite link for a lodge |
| `GET` | `/{invite_id}` | Public | Retrieve invite details (validates before tenant registers) |

### Dashboards
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/dashboard-landlord/{lodge_id}` | Landlord | Full lodge analytics (financials, room grid, entity counts) |
| `GET` | `/api/v1/dashboard-tenant` | Tenant | Personal lease and payment summary |

### Health
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/healthy` | Public | Server health check |

---

## 📁 Project Structure

```
backend/
├── alembic/                       # Versioned database migration scripts
├── app/
│   ├── main.py                    # Application entry point, middleware, and router registration
│   ├── api/
│   │   ├── deps.py                # Shared FastAPI dependencies (auth, DB session injection)
│   │   └── v1/
│   │       ├── user.py            # Auth endpoints (register, login, logout, refresh, me)
│   │       ├── lodges.py          # Lodge management endpoints
│   │       ├── rooms.py           # Room management endpoints
│   │       ├── tenants.py         # Tenant profile endpoints
│   │       ├── leases.py          # Lease lifecycle endpoints
│   │       ├── payments.py        # Payment recording endpoints
│   │       ├── invites.py         # Invite generation and retrieval endpoints
│   │       └── dashboards/
│   │           ├── landlord_dashboard.py  # Landlord analytics endpoints
│   │           └── tenant_dashboard.py   # Tenant summary endpoints
│   ├── core/
│   │   ├── config.py              # Pydantic-settings for environment variable loading
│   │   ├── constants.py           # Application-wide constants
│   │   ├── enums.py               # Enum definitions (UserRole, RoomStatus, LeaseStatus, etc.)
│   │   ├── exceptions.py          # Custom domain exception classes
│   │   ├── handlers.py            # Global FastAPI exception handlers
│   │   └── security.py            # Password hashing (Bcrypt) and JWT generation (PyJWT)
│   ├── crud/
│   │   ├── base_crud.py           # Generic base CRUD class (get, update, delete)
│   │   ├── user.py                # User and refresh token DB operations
│   │   ├── invite.py              # Invite DB operations
│   │   ├── lodge.py               # Lodge DB operations including financial aggregations
│   │   ├── room.py                # Room DB operations and bulk rent updates
│   │   ├── tenantprofile.py       # Tenant profile DB operations
│   │   ├── lease.py               # Lease DB operations and active-lease queries
│   │   └── payment.py             # Payment DB operations and balance calculations
│   ├── db/
│   │   ├── base.py                # SQLAlchemy Declarative Base
│   │   └── session.py             # Database session factory and FastAPI dependency
│   ├── models/
│   │   ├── user.py                # User ORM model
│   │   ├── refresh_token.py       # RefreshToken ORM model
│   │   ├── invitation.py          # Invite ORM model (UUID pk, expiry, status)
│   │   ├── lodge.py               # Lodge ORM model
│   │   ├── room.py                # Room ORM model
│   │   ├── tenantprofile.py       # TenantProfile ORM model
│   │   ├── lease.py               # Lease ORM model — computed_status @property
│   │   └── payment.py             # Payment ORM model (append-only)
│   ├── schemas/
│   │   ├── user.py                # User DTOs — UserCreate, UserResponse, UserUpdate, Token
│   │   ├── invitation.py          # Invite DTOs — InviteCreate, InviteResponse, InviteDetail
│   │   ├── lodge.py               # Lodge DTOs — LodgeCreate (with RoomGenerator), LodgeResponse
│   │   ├── room.py                # Room DTOs — RoomCreate, RoomUpdate, RoomGridSummary, BulkRoomUpdate
│   │   ├── tenantprofile.py       # Tenant DTOs — TenantProfileCreate, TenantProfileResponse
│   │   ├── lease.py               # Lease DTOs — LeaseCreate, LeaseUpdate (restricted), LeaseResponse
│   │   ├── payment.py             # Payment DTOs — PaymentCreate, PaymentResponse
│   │   ├── dashboard.py           # Full dashboard response schemas (Landlord + Tenant)
│   │   ├── entity_count.py        # Room and tenant count summary schemas
│   │   ├── financial.py           # Financial aggregation response schemas
│   │   ├── error.py               # Standardised error response schema
│   │   └── generic_extras.py      # Shared internal schema components
│   └── services/
│       ├── user_service.py        # Auth logic — registration, login, token rotation, logout
│       ├── invite_service.py      # Invite validation and expiry logic
│       ├── lodge_service.py       # Lodge creation and ownership verification logic
│       ├── room_service.py        # Room availability, status, and existence checks
│       ├── tenant_services.py     # Tenant onboarding, approval, and profile update logic
│       ├── lease_services.py      # Lease creation, termination, and tenant appeal logic
│       ├── payment_service.py     # Payment recording and outstanding balance logic
│       └── dashboard_service.py   # Dashboard data aggregation and orchestration
├── test/
│   ├── conftest.py                # Pytest fixtures and isolated in-memory test DB setup
│   ├── test_auth.py               # Authentication flow tests (14 tests)
│   ├── test_lodge.py              # Lodge management tests
│   ├── test_room.py               # Room management tests
│   ├── test_tenant.py             # Tenant profile and approval tests
│   ├── test_lease.py              # Lease lifecycle tests
│   ├── test_payment.py            # Payment recording tests
│   └── test_main.py               # Application startup tests
├── utilities/
│   └── dashboard_utilities.py     # Dashboard filtering helpers
├── System_Flow.md                 # Source of truth for all API user flows
├── .env.example                   # Environment variable template
├── alembic.ini                    # Alembic migration configuration
├── pytest.ini                     # Pytest configuration with coverage settings
├── requirements.txt               # Python package dependencies
└── test_main.http                 # Manual HTTP request collection for API testing
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher

### 1. Clone and Setup

```powershell
# Clone the repository
git clone https://github.com/DonaldXoftDev/LodgeManagerAPIProject.git
cd LodgeManagerAPIProject/backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy the environment template
Copy-Item .env.example .env
```

Open `.env` and fill in your values (see [Environment Variables](#-environment-variables)).

### 3. Run Database Migrations

```powershell
alembic upgrade head
```

### 4. Start the Server

```powershell
uvicorn app.main:app --reload
```

### Accessing the API
Once running:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/healthy](http://localhost:8000/healthy)

---

## ⚙ Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | `sqlite:///./lodge_manager.db` | Database connection string |
| `SECRET_KEY` | ✅ | — | Secret key for signing access tokens. Generate with: `openssl rand -hex 32` |
| `REFRESH_SECRET_KEY` | ✅ | — | Separate secret key for signing refresh tokens |
| `ALGORITHM` | ❌ | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `30` | Access token expiry in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | `7` | Refresh token expiry in days |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore` by default.

---

## 🧪 Running Tests

The test suite uses an isolated in-memory SQLite database so no production data is ever touched.

```powershell
.\.venv\Scripts\python.exe -m pytest test/ -v --cov=app
```

---

## 🤝 Contributing

Feedback, suggestions, and contributions are very welcome. Feel free to open an issue or submit a pull request.
