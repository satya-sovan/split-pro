# SplitPro Backend (FastAPI + MariaDB)

Backend API for SplitPro expense splitting application, migrated from Next.js/tRPC to FastAPI/REST.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MariaDB 11.0+
- Redis 7+ (for Celery tasks)

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings
# At minimum, set:
# - DATABASE_URL
# - SECRET_KEY
```

### Database Setup

```bash
# Start MariaDB and Redis with Docker
docker-compose up -d

# Run database migrations
alembic upgrade head
```

### Run Development Server

```bash
# Start FastAPI with auto-reload
uvicorn app.main:app --reload

# Or use Python directly
python app/main.py
```

Server will start at: http://localhost:8000

## 📚 API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🗄️ Database

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

### Reset Database

```bash
# Drop all tables and recreate
alembic downgrade base
alembic upgrade head
```

## 🔐 Authentication

### JWT Tokens

The API uses JWT Bearer tokens for authentication.

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

**Use Token:**
```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Magic Link

Passwordless authentication via email:

```bash
# Request magic link
curl -X POST http://localhost:8000/api/auth/magic-link \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Verify magic link token
curl -X POST http://localhost:8000/api/auth/magic-link/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "..."}'
```

## 📝 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login with email/password |
| POST | `/magic-link` | Send magic link email |
| POST | `/magic-link/verify` | Verify magic link |
| GET | `/google` | Google OAuth redirect |
| GET | `/google/callback` | OAuth callback |

### Expenses (`/api/expenses`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create expense |
| PUT | `/{id}` | Update expense |
| DELETE | `/{id}` | Delete expense |
| GET | `/{id}` | Get expense details |
| GET | `/` | List expenses |
| GET | `/balances/all` | Get all balances |
| POST | `/currency-conversion` | Create conversion |

### Groups (`/api/groups`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create group |
| GET | `/` | List groups |
| GET | `/{id}` | Get group details |
| PUT | `/{id}` | Update group |
| POST | `/join` | Join by public ID |
| POST | `/{id}/members` | Add member |
| DELETE | `/{id}/members/{user_id}` | Remove member |

### Users (`/api/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Get current user |
| PUT | `/me` | Update preferences |
| GET | `/friends` | List friends |
| GET | `/{id}` | Get user details |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_expenses.py

# Run in watch mode
pytest-watch
```

## 🛠️ Development

### Code Quality

```bash
# Format code with Black
black app/

# Lint with flake8
flake8 app/

# Type check with mypy
mypy app/
```

### Project Structure

```
app/
├── api/              # API layer
│   ├── routers/      # Endpoint handlers
│   └── deps.py       # Dependencies (auth, db)
├── core/             # Core functionality
│   ├── config.py     # Settings
│   ├── database.py   # DB connection
│   └── security.py   # Auth logic
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── utils/            # Utilities
```

### Adding New Endpoint

1. **Create schema** in `app/schemas/`
2. **Create service** in `app/services/`
3. **Create router** in `app/api/routers/`
4. **Register router** in `app/main.py`
5. **Write tests** in `tests/`

Example:

```python
# app/api/routers/example.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/")
async def get_examples(current_user = Depends(get_current_user)):
    return {"message": "Hello!"}

# app/main.py
from app.api.routers import example
app.include_router(example.router, prefix="/api")
```

## 🔄 Migration from TypeScript

This backend replaces the Next.js/tRPC API. Key differences:

| TypeScript (tRPC) | Python (FastAPI) |
|-------------------|------------------|
| `trpc.expense.create.mutate()` | `POST /api/expenses` |
| End-to-end type safety | Manual type definitions |
| Prisma ORM | SQLAlchemy ORM |
| PostgreSQL | MariaDB |
| NextAuth.js | Custom JWT |
| BigInt literals (`1250n`) | Python int (`1250`) |

### Maintaining Type Safety

Generate TypeScript types from OpenAPI:

```bash
# In frontend directory
npm install openapi-typescript-codegen --save-dev
npx openapi-typescript-codegen \
  --input http://localhost:8000/api/openapi.json \
  --output ./src/api
```

## 🐳 Docker

### Development

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Production

```bash
# Build production image
docker build -t splitpro-backend .

# Run production container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=mysql+pymysql://... \
  splitpro-backend
```

## 📊 Database Schema

### Core Tables

- `users` - User accounts
- `accounts` - OAuth accounts
- `groups` - Expense groups
- `expenses` - Individual expenses
- `expense_participants` - Who owes what
- `balance_view` - Calculated balances

### Key Relationships

```
User ─┬─ owns → Group
      ├─ member of → GroupUser → Group
      ├─ paid → Expense
      ├─ participant in → ExpenseParticipant → Expense
      └─ balances → BalanceView
```

## 💰 Number Handling

All amounts are stored as **integers (cents)** to avoid floating point errors:

```python
from app.utils.numbers import get_currency_helpers

helpers = get_currency_helpers("USD", "en-US")

# Convert display string to cents
amount = helpers.to_safe_bigint("12.50")  # 1250

# Convert cents to display string
display = helpers.to_ui_string(1250)  # "USD 12.50"
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MariaDB connection string | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `DEBUG` | Debug mode | False |
| `CORS_ORIGINS` | Allowed origins | localhost:3000 |
| `REDIS_URL` | Redis connection | redis://localhost:6379 |
| `SMTP_HOST` | Email server | smtp.gmail.com |
| `GOOGLE_CLIENT_ID` | Google OAuth | Optional |
| `R2_BUCKET_NAME` | S3/R2 storage | Optional |

See `.env.example` for full list.

## 🐛 Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server...")
```

**Solution**: Ensure MariaDB is running:
```bash
docker-compose up -d mariadb
```

### JWT Decode Error

```
HTTPException: Invalid authentication credentials
```

**Solution**: Token expired or invalid SECRET_KEY. Login again.

### Import Error

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Activate virtual environment and install dependencies:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

## 📈 Performance

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_expense_group ON expenses(group_id);
CREATE INDEX idx_expense_paid_by ON expenses(paid_by);
CREATE INDEX idx_balance_user ON balance_view(user_id);
```

### Connection Pooling

Configured in `app/core/database.py`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pre-ping: Enabled (checks connection health)

## 📞 Support

- **Documentation**: See `MIGRATION_STATUS.md` and `MIGRATION_GUIDE.md`
- **API Docs**: http://localhost:8000/api/docs
- **Issues**: Check logs and error messages

## 📄 License

Same as original SplitPro project - check root LICENSE file.

---

Built with ❤️ using FastAPI, SQLAlchemy, and MariaDB

