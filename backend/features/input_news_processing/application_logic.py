import asyncio
from datetime import datetime

from core.engine import get_session_context
from features.input_news_processing.schemas import InputNewsSchema
from features.input_news_processing.testing_data.additional_input_news import ADDITIONAL_ARTICLES
from features.input_news_processing.testing_data.common import load_testing_input_news_data
from features.input_news_processing.testing_data.initial_input_news import INITIAL_INPUT_ARTICLES
from services.input_news_service import InputNewsService


_mock_data = iter([
    load_testing_input_news_data(INITIAL_INPUT_ARTICLES),
    load_testing_input_news_data(ADDITIONAL_ARTICLES)
])

async def parse_news(from_date: datetime, to_date: datetime) -> None:
    # 1. Call function to get the data, for now mocked
    input_news: list[InputNewsSchema] = next(_mock_data, [])
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session)
        await input_news_service.add_input_news_batch(input_news_list=input_news)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(parse_news(0, 0))
    print(result)

    loop.close()
