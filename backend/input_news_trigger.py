import asyncio
import os
import pathlib
import tempfile
from datetime import datetime, timedelta

from core.engine import get_session_context
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import NewsResponseDetailed
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.ai_library.openai_model import OpenAIModel
from features.input_news_processing.archive.local_archive import LocalArchive

from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService


def verify_generated_news(generated_news: list[NewsResponseDetailed]) -> None:
    for single_generated_news in generated_news:
        content_len = len(single_generated_news.content.split(" "))
        json_dump = single_generated_news.model_dump_json()
        assert content_len >= 150, f"News {json_dump} don't have minimum 200 words in content. Len of content: {content_len}"
        assert 1 <= len(
            single_generated_news.tags) <= 3, f"News {json_dump} don't have minimum of 2 and maximum of 3 tags. Len of tags: {len(single_generated_news.tags)}"


async def get_input_news_and_parse(adjust_parse_date: bool = True, delta: timedelta = timedelta(days=1)):
    """ Official scenario that will be used to parse new input news and generates the parsed ones from them"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")
    tmp_dir = tempfile.mkdtemp()
    # TODO: Implement local archive target directory
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        if adjust_parse_date:
            latest_timestamp = await input_news_service.get_latest_timestamp()
            if latest_timestamp is not None:
                now = datetime.utcnow()
                time_since_latest = now - latest_timestamp

                if time_since_latest < delta:
                    delta = time_since_latest
        await input_news_service.scrap_and_save_input_news(delta=delta)

    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(session=session, archive=local_archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        await input_news_service.scrap_and_save_input_news(delta=delta)
        session.flush()
        await article_generation_service.connect_existing_news(delta=delta)
        session.flush()
        await article_generation_service.creates_new_news(delta=delta)


async def test_parse_news(commit_transaction: bool = False):
    """ Testing workflow, change commit transaction to True if you want to check generated news on page or in DB """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")
    delta = timedelta(days=365)
    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
    async with get_session_context(commit_transaction=commit_transaction) as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(session=session, archive=local_archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        parsed_news_service = NewsService(session=session)
        initial_tags_len = len(await parsed_news_service.get_tags())
        print("Loading initial data")
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        assert len(
            input_news) == 10, f"Application didn't load proper input news. Loaded {len(input_news)}, Expected 10"
        print(f"Input news loaded: {input_news}")
        await session.flush()
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 0, f"The testing workflow shouldn't add any connected news. {generated_news=}"
        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 3, f"Service should generate exactly 3 news. {generated_news=}"
        await session.flush()
        print("Loading additional news.")
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        print(f"Input news loaded: {input_news}")
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"The testing workflow should add exactly 1 connected news. {generated_news=}"
        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"Service should generate exactly 1 news. {generated_news=}"
        await session.flush()
        end_tags_len = len(await parsed_news_service.get_tags())
        # assert initial_tags_len == end_tags_len, (
        #    f"Tests created tags even when was expected that will be used the existing ones."
        #    f"Number of initial tags: {initial_tags_len} Number of the end tags: {end_tags_len}")


async def generate_picture_for_news(news_id: int, commit_transaction: bool = False) -> None:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")
    delta = timedelta(days=365)
    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
    async with get_session_context(commit_transaction=commit_transaction) as session:
        article_generation_service = ArticleGenerationService(session=session, archive=local_archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        await article_generation_service.generate_picture_for_news(news_id=news_id)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(generate_picture_for_news(news_id=74))
    print(result)

    loop.close()
