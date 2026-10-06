"""Metrics and funnel observability router."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.db.session import get_db
from sentinel.app.models import ItemModel

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics(session: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    item_count_res = await session.execute(select(ItemModel))
    items = list(item_count_res.scalars().all())
    must_know = sum(1 for it in items if it.priority == "MUST_KNOW")
    should_know = sum(1 for it in items if it.priority == "SHOULD_KNOW")

    return {
        "total_items_indexed": len(items),
        "must_know_count": must_know,
        "should_know_count": should_know,
        "cost_incurred_usd": 0.0,
    }
