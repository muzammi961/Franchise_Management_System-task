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

## 📋 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/login` | Login (Super Admin or Franchise) |
| `POST` | `/api/v1/auth/refresh-token`  | Refresh access token |
| `POST` | `/api/v1/auth/logout` |  Logout & blacklist token |
| `POST` | `/api/v1/auth/send-otp`  | Send OTP to email |
| `POST` | `/api/v1/auth/verify-otp`  | Verify OTP |

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
| `GET` | `/api/v1/profile`  | Get current user profile |
| `PUT` | `/api/v1/profile` | Update profile (name, phone, address, password) |

## 🧪 Running Tests

```bash
pytest -v
```

Tests use an **SQLite in-memory database** — no PostgreSQL or Redis required for testing.  
Redis and SMTP calls in OTP tests are **mocked**.
