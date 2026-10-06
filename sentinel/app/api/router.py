"""Unified API Router combining health, metrics, telegram webhook, and admin endpoints."""

from fastapi import APIRouter
from sentinel.app.api.health import router as health_router
from sentinel.app.api.metrics import router as metrics_router
from sentinel.app.api.telegram import router as telegram_router
from sentinel.app.api.admin import router as admin_router
from sentinel.app.api.dashboard import router as dashboard_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(telegram_router)
api_router.include_router(admin_router)
