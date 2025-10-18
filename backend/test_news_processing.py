#!/usr/bin/env python
import argparse
import asyncio
import os
import pathlib
import tempfile
from datetime import timedelta

import structlog

from core.domain.schemas import ParsedNewsResponseDetailed
from core.engine import get_session_context
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.domain.article_generation_service import (
    ArticleGenerationService,
)
from features.input_news_processing.domain.input_news_service import InputNewsService
from features.input_news_processing.testing_data.common import mock_data

logger = structlog.get_logger()

CHARACTER_LENGTH = 150
TAGS_LENGTH = 3


def verify_generated_news(generated_news: list[ParsedNewsResponseDetailed]) -> None:
    """Verify that generated news meets the quality criteria"""
    for single_generated_news in generated_news:
        content_len = len(single_generated_news.content.split(" "))
        json_dump = single_generated_news.model_dump_json()
        assert content_len >= CHARACTER_LENGTH, (
            f"News {json_dump} don't have minimum 150 words in content. Len of content: {content_len}"
        )
        assert 1 <= len(single_generated_news.tags) <= TAGS_LENGTH, (
            f"News {json_dump} don't have minimum of 1 and maximum of 3 tags. "
            f"Len of tags: {len(single_generated_news.tags)}"
        )


async def test_parse_news(commit_transaction: bool = False) -> None:
    """Testing workflow for news parsing and generation"""
    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))

    async with get_session_context(commit_transaction=commit_transaction) as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
        )

        logger.info("Loading initial data")

        # First batch of input news
        input_news_raw = next(mock_data, [])
        input_news = await input_news_service.add_or_update_input_news_batch(input_news_list=input_news_raw)
        input_news_ids = [news.id for news in input_news]
        input_news_older = await input_news_service.get_input_news_by_delta(
            delta=timedelta(days=1000), has_parsed_news=False
        )
        input_news_ids += [news.id for news in input_news_older if news.id not in input_news_ids]
        input_news_count = 10
        assert len(input_news) == input_news_count, (
            f"Application didn't load proper input news. Loaded {len(input_news)}, Expected 10"
        )
        logger.info(f"Input news loaded: {input_news}")
        await session.flush()

        # First batch of news generation
        generated_news = await article_generation_service.connect_input_news_to_existing_articles(
            input_news_ids=input_news_ids
        )
        assert len(generated_news) == 0, f"The testing workflow shouldn't add any connected news. {generated_news=}"

        generated_news_groups = await article_generation_service.choose_input_news_for_new_articles(
            input_news_ids=input_news_ids
        )
        news_count = 3
        assert len(generated_news) == news_count, f"Service should generate exactly 3 news. {generated_news=}"
        await session.flush()
        for generated_news_group in generated_news_groups:
            new_article = await article_generation_service.create_new_article_from_input_news(
                input_news_ids=generated_news_group.input_news_ids, importancy=generated_news_group.importancy
            )
            verify_generated_news([new_article])

        # Second batch of input news
        logger.info("Loading additional news.")
        input_news_raw = next(mock_data, [])
        input_news = await input_news_service.add_or_update_input_news_batch(input_news_list=input_news_raw)
        input_news_ids = [news.id for news in input_news]
        input_news_older = await input_news_service.get_input_news_by_delta(
            delta=timedelta(days=1000), has_parsed_news=False
        )
        input_news_ids += [news.id for news in input_news_older if news.id not in input_news_ids]
        logger.info(f"Input news loaded: {input_news}")

        # Second batch of news generation
        generated_news = await article_generation_service.connect_input_news_to_existing_articles(
            input_news_ids=input_news_ids
        )
        assert len(generated_news) == 1, f"The testing workflow should add exactly 1 connected news. {generated_news=}"
        for single_generated_news in generated_news:
            new_article = await article_generation_service.enrich_existing_article(single_generated_news)
            verify_generated_news([new_article])
        generated_news_groups = await article_generation_service.choose_input_news_for_new_articles(
            input_news_ids=input_news_ids
        )
        assert len(generated_news) == 1, f"Service should generate exactly 1 news. {generated_news=}"
        await session.flush()
        for generated_news_group in generated_news_groups:
            new_article = await article_generation_service.create_new_article_from_input_news(
                input_news_ids=generated_news_group.input_news_ids, importancy=generated_news_group.importancy
            )
            verify_generated_news([new_article])

        # Verify tags
        # end_tags_len = len(await parsed_news_service.get_tags())
        # Uncomment if you want to check for tag reuse
        # assert initial_tags_len == end_tags_len, (
        #    f"Tests created tags even when was expected that will be used the existing ones."
        #    f"Number of initial tags: {initial_tags_len} Number of the end tags: {end_tags_len}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test News Processing Functionality")
    parser.add_argument("--commit", action="store_true", help="Commit transactions to database")
    parser.add_argument("--days", type=int, default=365, help="Number of days to look back for news")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_parse_news(commit_transaction=args.commit))
    logger.info("Tests completed successfully!")


if __name__ == "__main__":
    main()
