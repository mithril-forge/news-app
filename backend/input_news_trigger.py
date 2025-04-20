import asyncio
from datetime import datetime, timedelta

from core.engine import get_session_context

from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.testing_data.additional_input_news import ADDITIONAL_ARTICLES
from features.input_news_processing.testing_data.common import load_testing_input_news_data
from features.input_news_processing.testing_data.initial_input_news import INITIAL_INPUT_ARTICLES


_mock_data = iter([
    load_testing_input_news_data(INITIAL_INPUT_ARTICLES),
    load_testing_input_news_data(ADDITIONAL_ARTICLES)
])


async def parse_news():
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session)
        session.flush()
        article_generation_service = ArticleGenerationService(session=session)
        await input_news_service.parse_input_news(0, 0)
        await article_generation_service.creates_new_articles(timedelta_back=timedelta(days=360))
        await input_news_service.parse_input_news(0, 0)
        await article_generation_service.creates_new_articles(timedelta_back=timedelta(days=7))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(parse_news())
    print(result)

    loop.close()
