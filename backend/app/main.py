"""
Main FastAPI application
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routers import auth, expense, group, user, bank, health

# Import all models to ensure they are registered with Base.metadata
from app.models import models  # noqa: F401

# Configure logging to stdout with prefix for docker logs
logging.basicConfig(
    level=logging.INFO,
    format='[BACKEND] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configure uvicorn access log format
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.handlers = [logging.StreamHandler(sys.stdout)]
for handler in uvicorn_access.handlers:
    handler.setFormatter(logging.Formatter('[BACKEND] %(asctime)s - %(message)s'))

# Configure uvicorn error log format
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.handlers = [logging.StreamHandler(sys.stdout)]
for handler in uvicorn_error.handlers:
    handler.setFormatter(logging.Formatter('[BACKEND] %(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler - runs on startup and shutdown.
    Creates database tables if they don't exist (like Hibernate's create-if-not-exists).
    """
    # Startup: Create all tables that don't exist
    logger.info("Starting up - checking database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    yield  # Application runs here

    # Shutdown: cleanup if needed
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="SAHASplit - Expense splitting application API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(expense.router, prefix="/api")
app.include_router(group.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(bank.router, prefix="/api")
app.include_router(health.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - redirects to docs"""
    return {
        "message": "SAHASplit API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "api": "/api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

