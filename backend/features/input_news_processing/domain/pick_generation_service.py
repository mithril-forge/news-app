import datetime

from core.models import NewsPick, NewsPickItem
from core.repository import AsyncBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PickGenerationService:
    def __init__(self, session: AsyncSession):
        self.pick_repository = AsyncBaseRepository[NewsPick](session, NewsPick)
        self.pick_connection_repository = AsyncBaseRepository[NewsPickItem](session, NewsPickItem)

    async def save_pick(self, account_id: int, date: datetime.date, description: str) -> int:
        pick = await self.pick_repository.add({"date": date, "account_id": account_id, "description": description})
        if pick.id is None:
            raise ValueError("Pick should have correct id")
        return pick.id

    async def connect_news_to_pick(self, pick_id: int, news_ids: list[int]) -> None:
        for news_id in news_ids:
            await self.pick_connection_repository.add({"pick_id": pick_id, "parsed_news_id": news_id})
