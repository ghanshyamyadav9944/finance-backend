# Finance Dashboard API

A backend system for a finance dashboard with role-based access control, built with FastAPI + SQLite + JWT.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite + SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Server**: Uvicorn

## Project Structure
```
backend/
├── main.py          # App entry point
├── database.py      # Database connection
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── routes/          # API endpoints
├── core/            # JWT & security
└── requirements.txt
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/finance-backend.git
cd finance-backend
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Open Swagger docs
```
http://127.0.0.1:8000/docs
```

## API Endpoints

### Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /auth/register | Public | Register new user |
| POST | /auth/login | Public | Login and get JWT token |

### Transactions
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /transactions | Admin | Create transaction |
| GET | /transactions | All roles | Get all transactions |
| PUT | /transactions/{id} | Admin | Update transaction |
| DELETE | /transactions/{id} | Admin | Soft delete transaction |

### Dashboard
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /dashboard/summary | Admin, Analyst | Total income, expense, balance |
| GET | /dashboard/category | Admin, Analyst | Category wise totals |
| GET | /dashboard/trends | Admin, Analyst | Monthly trends |
| GET | /dashboard/recent | Admin, Analyst | Recent 10 transactions |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /users | Admin | List all users |
| PATCH | /users/{id}/status | Admin | Activate/deactivate user |

## Roles and Permissions

| Role | Permissions |
|------|-------------|
| Admin | Full access - manage users, create/edit/delete transactions |
| Analyst | View transactions + access dashboard summaries |
| Viewer | Only view transactions |

## How to Test

### Step 1 - Register an admin user
```json
POST /auth/register
{
  "name": "Ghanshyam",
  "email": "admin@gmail.com",
  "password": "test123",
  "role": "admin"
}
```

### Step 2 - Login to get token
```json
POST /auth/login
{
  "email": "admin@gmail.com",
  "password": "test123"
}
```

### Step 3 - Use token in Swagger
Click Authorize button in Swagger UI
Enter: Bearer YOUR_TOKEN_HERE

### Step 4 - Create a transaction
```json
POST /transactions
{
  "amount": 5000,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "notes": "Monthly salary"
}
```

## Assumptions

- SQLite is used for simplicity. Can be replaced with PostgreSQL for production.
- Soft delete is implemented for transactions (is_deleted flag).
- JWT tokens expire after 30 minutes.
- Passwords are hashed using bcrypt.
- Role based access is enforced at API level using FastAPI dependencies.

## Author

Ghanshyam | B.Tech CSE | AKTU
Assignment for Zorvyn Fintech - Backend Developer Intern
