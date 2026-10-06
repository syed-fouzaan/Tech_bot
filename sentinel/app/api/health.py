"""Health and readiness router."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.db.session import get_db
from sentinel.app.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "sentinel", "version": "2.1.0"}


@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    try:
        await session.execute(select(1))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "ready" if db_healthy else "degraded",
        "database": db_healthy,
        "daily_budget_usd": settings.DAILY_AI_BUDGET,
        "paid_providers_allowed": settings.ALLOW_PAID_PROVIDERS,
        "budget_invariant_passed": (settings.DAILY_AI_BUDGET == 0.0 and not settings.ALLOW_PAID_PROVIDERS),
    }
