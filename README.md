# 🚀 FastAPI JWT Authentication with Super Admin & Franchise Management System

A production-ready FastAPI backend featuring JWT authentication, role-based access control,
franchise CRUD, OTP via SMTP, Redis caching, and WebSocket real-time notifications.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy (Sync ORM) |
| Authentication | JWT (python-jose) + bcrypt (passlib) |
| Caching / OTP | Redis (async) |
| Email / OTP | SMTP via aiosmtplib |
| Real-time | WebSocket (FastAPI native) |
| Testing | pytest + pytest-asyncio + httpx |

---

## 📁 Project Structure

```
Franchise_management_system_task/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   └── franchise.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── franchise.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── franchise.py
│   │   ├── profile.py
│   │   └── websocket.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── franchise_service.py
│   │   └── otp_service.py
│   ├── utils/
│   │   ├── jwt.py
│   │   ├── otp.py
│   │   ├── redis.py
│   │   └── smtp.py
│   ├── middleware/
│   │   └── auth_middleware.py
│   └── dependencies/
│       └── role_checker.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_franchise.py
│   └── test_otp.py
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL running locally
- Redis running locally

### 2. Clone & enter the project

```bash
cd Franchise_management_system_task
```

### 3. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux / macOS
```

Edit `.env` and fill in:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/franchise_db
SECRET_KEY=your-super-secret-key-min-32-chars
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
REDIS_URL=redis://localhost:6379/0
```

### 6. Create the PostgreSQL database

```sql
CREATE DATABASE franchise_db;
```

### 7. Seed the Super Admin (one-time)

Open a Python shell in the project root:

```python
from app.core.database import SessionLocal, create_tables
from app.models.user import User, UserRole
from app.core.security import hash_password

create_tables()
db = SessionLocal()
admin = User(
    email="admin@yourcompany.com",
    password=hash_password("Admin@1234"),
    role=UserRole.SUPER_ADMIN,
    is_active=True,
)
db.add(admin)
db.commit()
db.close()
print("Super admin created.")
```

---

## ▶️ Run Locally

```bash
uvicorn app.main:app --reload
```

- Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc    → [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health   → [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔌 WebSocket

Connect to real-time notifications:

```
ws://localhost:8000/ws/notifications
```

Events broadcast:
- `CONNECTED` — on connect
- `LOGIN_SUCCESS` — after a user logs in
- `OTP_VERIFIED` — after OTP verification
- `FRANCHISE_CREATED` / `FRANCHISE_UPDATED` / `FRANCHISE_DELETED`
- Send `ping` → receive `PONG`

---

## 📋 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/login` | ❌ | Login (Super Admin or Franchise) |
| `POST` | `/api/v1/auth/refresh-token` | ❌ | Refresh access token |
| `POST` | `/api/v1/auth/logout` | ✅ | Logout & blacklist token |
| `POST` | `/api/v1/auth/send-otp` | ❌ | Send OTP to email |
| `POST` | `/api/v1/auth/verify-otp` | ❌ | Verify OTP |

**Super Admin Login:**
```json
{
  "email": "admin@yourcompany.com",
  "password": "Admin@1234"
}
```

**Franchise Login:**
```json
{
  "email": "franchise@example.com",
  "password": "Franchise@1234",
  "franchise_code": "FRAN-001"
}
```

---

### 🏢 Franchise (Super Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/franchise` | Create franchise |
| `GET` | `/api/v1/franchise?page=1&limit=10&search=kochi` | List with pagination & search |
| `GET` | `/api/v1/franchise/{id}` | Get by ID |
| `PUT` | `/api/v1/franchise/{id}` | Update (franchise_code is immutable) |
| `DELETE` | `/api/v1/franchise/{id}` | Delete |

**Create Franchise:**
```json
{
  "name": "Kochi Branch",
  "email": "kochi@example.com",
  "password": "Kochi@1234",
  "phone": "9876543210",
  "address": "MG Road, Kochi, Kerala",
  "franchise_code": "KOCHI-001"
}
```

---

### 👤 Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/profile` | ✅ | Get current user profile |
| `PUT` | `/api/v1/profile` | ✅ | Update profile (name, phone, address, password) |

---

## 🔑 JWT Details

- **Access token** expires in 30 minutes  
- **Refresh token** expires in 7 days  
- Both tokens contain: `user_id`, `email`, `role`, `exp`, `jti`  
- Logout blacklists the `jti` in Redis  
- Refresh tokens are rotated on use (old token is blacklisted)

---

## ⚡ Redis Keys

| Key Pattern | Purpose | TTL |
|---|---|---|
| `otp:{email}` | Stored OTP value | 5 minutes |
| `otp_limit:{email}` | OTP request count | 10 minutes |
| `blacklist:{jti}` | Revoked JWT tokens | Token TTL |
| `profile:{user_id}` | Cached user profile | 5 minutes |
| `franchise:{id}` | Cached franchise data | 5 minutes |

---

## 🧪 Running Tests

```bash
pytest -v
```

Tests use an **SQLite in-memory database** — no PostgreSQL or Redis required for testing.  
Redis and SMTP calls in OTP tests are **mocked**.

---

## 📬 Unified Response Format

All API responses follow:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {},
  "error": null
}
```

---

## 🔐 Security Features

- bcrypt password hashing
- JWT signature + expiry validation on every request
- Redis blacklist check on every request  
- RBAC: `SUPER_ADMIN` and `FRANCHISE` roles enforced per route
- CORS middleware configured
- Environment variables — no hardcoded secrets
