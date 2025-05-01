import asyncio
import pathlib
import tempfile
from datetime import datetime, timedelta

from core.engine import get_session_context
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import NewsResponseDetailed
from features.input_news_processing.archive.local_archive import LocalArchive

from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.testing_data.additional_input_news import ADDITIONAL_ARTICLES
from features.input_news_processing.testing_data.common import load_testing_input_news_data
from features.input_news_processing.testing_data.initial_input_news import INITIAL_INPUT_ARTICLES

def verify_generated_news(generated_news: list[NewsResponseDetailed]) -> None:
    for single_generated_news in generated_news:
        content_len = len(single_generated_news.content.split(" "))
        json_dump = single_generated_news.model_dump_json()
        assert content_len >= 200, f"News {json_dump} don't have minimum 200 words in content. Len of content: {content_len}"
        assert 1 <= len(single_generated_news.tags) <= 3, f"News {json_dump} don't have minimum of 2 and maximum of 3 tags. Len of tags: {len(single_generated_news.tags)}"


async def get_input_news_and_parse():
    """ Official scenario that will be used to parse new input news and generates the parsed ones from them"""
    # TODO: Load external input news in separate transaction and solve duplicates/record timedelta that is already parsed
    delta = timedelta(days=7)
    tmp_dir = tempfile.mkdtemp()
    # TODO: Implement local archive target directory
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(session=session, archive=local_archive)
        await input_news_service.scrap_and_save_input_news(delta=delta)
        session.flush()
        await article_generation_service.connect_existing_news(delta=delta)
        session.flush()
        await article_generation_service.creates_new_news(delta=delta)


async def test_parse_news():
    """ Testing workflow, change commit transaction to True if you want to check generated news on page or in DB """
    delta = timedelta(days=365)
    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
    async with get_session_context(commit_transaction=False) as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(session=session, archive=local_archive)
        parsed_news_service = NewsService(session=session)
        initial_tags_len = len(await parsed_news_service.get_tags())
        print("Loading initial data")
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        assert len(input_news) == 10, f"Application didn't load proper input news. Loaded {len(input_news)}, Expected 10"
        print(f"Input news loaded: {input_news}")
        session.flush()
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 0, f"The testing workflow shouldn't add any connected news. {generated_news=}"
        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 3, f"Service should generate exactly 3 news. {generated_news=}"
        session.flush()
        print("Loading additional news.")
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        print(f"Input news loaded: {input_news}")
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"The testing workflow should add exactly 1 connected news. {generated_news=}"
        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"Service should generate exactly 1 news. {generated_news=}"
        session.flush()
        end_tags_len = len(await parsed_news_service.get_tags())
        assert initial_tags_len == end_tags_len, (f"Tests created tags even when was expected that will be used the existing ones."
                                                                               f"Number of initial tags: {initial_tags_len} Number of the end tags: {end_tags_len}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(test_parse_news())
    print(result)

    loop.close()
