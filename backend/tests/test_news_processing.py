#!/usr/bin/env python
import asyncio
import argparse
import os
import pathlib
import tempfile
from datetime import timedelta

from core.engine import get_session_context
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import NewsResponseDetailed
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService


def verify_generated_news(generated_news: list[NewsResponseDetailed]) -> None:
    """Verify that generated news meets the quality criteria"""
    for single_generated_news in generated_news:
        content_len = len(single_generated_news.content.split(" "))
        json_dump = single_generated_news.model_dump_json()
        assert content_len >= 150, f"News {json_dump} don't have minimum 150 words in content. Len of content: {content_len}"
        assert 1 <= len(
            single_generated_news.tags) <= 3, f"News {json_dump} don't have minimum of 1 and maximum of 3 tags. Len of tags: {len(single_generated_news.tags)}"


async def test_parse_news(commit_transaction: bool = False, delta_days: int = 365):
    """ Testing workflow for news parsing and generation """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")

    delta = timedelta(days=delta_days)
    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))

    async with get_session_context(commit_transaction=commit_transaction) as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key)
        )
        parsed_news_service = NewsService(session=session)

        # Store initial tag count
        initial_tags_len = len(await parsed_news_service.get_tags())
        print("Loading initial data")

        # First batch of input news
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        assert len(
            input_news) == 10, f"Application didn't load proper input news. Loaded {len(input_news)}, Expected 10"
        print(f"Input news loaded: {input_news}")
        await session.flush()

        # First batch of news generation
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 0, f"The testing workflow shouldn't add any connected news. {generated_news=}"

        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 3, f"Service should generate exactly 3 news. {generated_news=}"
        await session.flush()

        # Second batch of input news
        print("Loading additional news.")
        input_news = await input_news_service.scrap_and_save_input_news(delta=delta)
        print(f"Input news loaded: {input_news}")

        # Second batch of news generation
        generated_news = await article_generation_service.connect_existing_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"The testing workflow should add exactly 1 connected news. {generated_news=}"

        generated_news = await article_generation_service.creates_new_news(delta=delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, f"Service should generate exactly 1 news. {generated_news=}"
        await session.flush()

        # Verify tags
        end_tags_len = len(await parsed_news_service.get_tags())
        # Uncomment if you want to check for tag reuse
        # assert initial_tags_len == end_tags_len, (
        #    f"Tests created tags even when was expected that will be used the existing ones."
        #    f"Number of initial tags: {initial_tags_len} Number of the end tags: {end_tags_len}")


def main():
    parser = argparse.ArgumentParser(description="Test News Processing Functionality")
    parser.add_argument("--commit", action="store_true", help="Commit transactions to database")
    parser.add_argument("--days", type=int, default=365, help="Number of days to look back for news")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_parse_news(commit_transaction=args.commit, delta_days=args.days))
        print("Tests completed successfully!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
