<p align="center" style="margin-top: 12px">
  <a href="https://sahasplit.app">
  <img width="100px"  style="border-radius: 50%;" src="https://sahasplit.app/logo_circle.png" alt="SAHASplit Logo">
  </a>

  <h1 align="center">SAHASplit</h1>
  <h2 align="center">An open source alternative to Splitwise</h2>
  <p align="center">
    <strong>🎉 Now with Unified Deployment - Single Container, Single URL!</strong>
  </p>


---

## 🎉 New Architecture: Python FastAPI + Vue.js

**This repository has been migrated to a modern Python + Vue.js stack!**

> **📦 Legacy Code:** The original Next.js/React implementation is preserved in the `.bak-project/` folder.

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Vue.js 3.4 + TypeScript + Vite |
| **Backend** | Python 3.11 + FastAPI |
| **Database** | MariaDB 11.0 |
| **Cache** | Redis 7 |
| **State** | Pinia |
| **Styling** | Tailwind CSS |
| **Deployment** | Docker + docker-compose |

---

## 🚀 Quick Start

**Single Container Deployment - Everything accessible at http://localhost**

```bash
# 1. Setup (first time only)
setup.bat

# 2. Start the application
start.bat
```

**That's it!** Access everything at:
- **Application:** http://localhost
- **API Documentation:** http://localhost/docs
- **API Endpoints:** http://localhost/api/*

---

**Development Mode** (separate services with hot reload):
```bash
start-dev.bat
```

- Frontend: http://localhost:3000 (hot reload)
- Backend: http://localhost:8000/docs

---

## About

SAHASplit is an open-source expense splitting application designed to be a complete replacement for Splitwise.

### ✨ Features

#### Core Features ✅
- ✅ Add expenses with individuals or groups
- ✅ Overall balances across groups
- ✅ Multiple currency support (20+ currencies)
- ✅ Upload expense bills (S3/R2)
- ✅ PWA support (installable web app)
- ✅ Split expenses unequally (share, percentage, exact amounts, adjustments)
- ✅ Push notifications
- ✅ Download your data (JSON export)
- ✅ Import from Splitwise
- ✅ Simplify group debts
- ✅ Community translations
- ✅ Currency conversion
- ✅ Recurring transactions
- ✅ Bank account transaction integration (Plaid + GoCardless)

#### Advanced Features
- Multi-currency balances
- Magic link authentication (passwordless)
- Google OAuth
- Email notifications
- Currency rate caching
- File storage (AWS S3 / Cloudflare R2)
- RESTful API with 48 endpoints
- Auto-generated API documentation

---

## 📚 Documentation

### Quick Links
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Implementation overview
- **[QUICKSTART_FULLSTACK.md](QUICKSTART_FULLSTACK.md)** - Detailed setup guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation index

### Additional Documentation
All detailed documentation has been organized in the `MD/` folder:
- Implementation guides
- Migration documentation
- Architecture details
- Developer guides
- Contributing guidelines

---

## 🏗️ Project Structure

```
split-pro/
├── frontend/              # Vue.js 3 + TypeScript + Vite
│   ├── src/
│   │   ├── views/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── stores/        # Pinia state management
│   │   ├── services/      # API client
│   │   └── router/        # Vue Router
│   └── Dockerfile
│
├── backend/               # Python 3.11 + FastAPI
│   ├── app/
│   │   ├── api/routers/   # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── models/        # SQLAlchemy models
│   │   └── schemas/       # Pydantic schemas
│   ├── docker-compose.yml # Full stack orchestration
│   └── Dockerfile
│
├── MD/                    # Documentation
├── .bak-project/          # Legacy Next.js code (archived)
└── README.md              # This file
```

---

## 🔧 Development

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.11+ (for backend development)

### Environment Setup

1. **Frontend** (optional for standalone dev):
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

2. **Backend** (with Docker):
```bash
cd backend
docker-compose up -d
```

Services:
- MariaDB: `localhost:3307`
- Redis: `localhost:6379`
- Backend: `localhost:8000`
- Frontend: `localhost:3000`

### API Documentation

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

All 48 endpoints are documented with request/response schemas.

---

## 🎯 Why This Migration?

### Original Implementation (Archived)
- Next.js 15 + React 19
- tRPC for type-safe APIs
- Prisma ORM + PostgreSQL
- Complex setup, high resource usage

### New Implementation ✨
- **Simpler Stack:** Vue.js is more approachable
- **Better Performance:** FastAPI is blazing fast
- **Lower Resources:** Python + MariaDB uses less memory
- **RESTful APIs:** Standard HTTP endpoints
- **Better Docs:** Auto-generated OpenAPI specs
- **Complete Features:** All original features + more

---

## 🐳 Docker Deployment

### Development
```bash
cd backend
docker-compose up
```

### Production
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Required for production:
- `DATABASE_URL` - MariaDB connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing key
- `R2_*` or `AWS_S3_*` - File storage credentials
- `SMTP_*` - Email configuration (optional)

See `.env.example` for full list.

---

## 🤝 Contributing

We welcome contributions! See [MD/CONTRIBUTING.md](MD/CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Original Splitwise team for the inspiration
- [spliit.app](https://spliit.app/) by Sebastien Castiel for the open-source alternative
- FastAPI and Vue.js communities for excellent frameworks
- All contributors and users

---

## 📞 Support

- **Documentation:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by the open-source community**

