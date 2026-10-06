"""Database access repositories."""

from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import ItemModel, WorkImpactLogModel


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_external_id(self, source_id: str, external_id: str) -> Optional[ItemModel]:
        stmt = select(ItemModel).where(
            (ItemModel.source_id == source_id) & (ItemModel.external_id == external_id)
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_latest_items(self, limit: int = 15) -> List[ItemModel]:
        stmt = select(ItemModel).order_by(ItemModel.importance_score.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_must_know_items(self, limit: int = 10) -> List[ItemModel]:
        stmt = select(ItemModel).where(ItemModel.priority == "MUST_KNOW").order_by(ItemModel.published_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())


class WinRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_wins(self, user_id: int) -> List[WorkImpactLogModel]:
        stmt = select(WorkImpactLogModel).where(WorkImpactLogModel.user_id == user_id).order_by(WorkImpactLogModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
