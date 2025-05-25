import asyncio
import os
import pathlib
import tempfile
import pytest
from datetime import timedelta

from core.engine import get_session_context
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import NewsResponseDetailed
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.testing_data.common import mock_data


def verify_generated_news(generated_news: list[NewsResponseDetailed]) -> None:
    """Verify that generated news meets quality requirements"""
    for single_generated_news in generated_news:
        content_len = len(single_generated_news.content.split(" "))
        json_dump = single_generated_news.model_dump_json()

        assert content_len >= 150, (
            f"News {json_dump} doesn't have minimum 150 words in content. "
            f"Content length: {content_len}"
        )

        assert 1 <= len(single_generated_news.tags) <= 3, (
            f"News {json_dump} doesn't have between 1 and 3 tags. "
            f"Number of tags: {len(single_generated_news.tags)}"
        )


class NewsProcessingTest:
    """Test class for news processing functionality"""

    def __init__(self, commit_transaction: bool = False):
        self.commit_transaction = commit_transaction
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key is None:
            raise ValueError("You need to provide GEMINI_API_KEY to use the model")

        self.delta = timedelta(days=365)
        self.tmp_dir = tempfile.mkdtemp()
        self.local_archive = LocalArchive(target_location=pathlib.Path(self.tmp_dir))

    async def test_parse_news_workflow(self):
        """Test the complete news parsing workflow"""
        async with get_session_context(commit_transaction=self.commit_transaction) as session:
            # Initialize services
            input_news_service = InputNewsService(session=session, archive=self.local_archive)
            article_generation_service = ArticleGenerationService(
                session=session,
                archive=self.local_archive,
                ai_model=GeminiAIModel(api_key=self.gemini_api_key)
            )
            parsed_news_service = NewsService(session=session)

            # Get initial state
            initial_tags_len = len(await parsed_news_service.get_tags())
            print(f"Initial number of tags: {initial_tags_len}")

            # Test first batch of mock data
            await self._test_first_batch(input_news_service, article_generation_service, session)

            # Test second batch of mock data
            await self._test_second_batch(input_news_service, article_generation_service, session)

            # Verify final state
            end_tags_len = len(await parsed_news_service.get_tags())
            print(f"Final number of tags: {end_tags_len}")

            print("All tests passed successfully!")

    async def _test_first_batch(self, input_news_service, article_generation_service, session):
        """Test first batch of mock data"""
        print("Loading initial data...")
        mocked_news = next(mock_data)
        input_news = await input_news_service.add_or_update_input_news_batch(
            input_news_list=mocked_news
        )

        # Verify input news loaded correctly
        assert len(input_news) == 10, (
            f"Application didn't load proper input news. "
            f"Loaded {len(input_news)}, Expected 10"
        )
        print(f"Input news loaded: {len(input_news)} articles")

        await session.flush()

        # Test connecting existing news (should be 0 for first run)
        generated_news = await article_generation_service.connect_existing_news(delta=self.delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 0, (
            f"The testing workflow shouldn't add any connected news. "
            f"Generated: {len(generated_news)}"
        )

        # Test creating new news
        generated_news = await article_generation_service.creates_new_news(delta=self.delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 3, (
            f"Service should generate exactly 3 news articles. "
            f"Generated: {len(generated_news)}"
        )

        await session.flush()
        print("First batch test completed successfully.")

    async def _test_second_batch(self, input_news_service, article_generation_service, session):
        """Test second batch of mock data"""
        print("Loading additional news...")
        mocked_news = next(mock_data)
        input_news = await input_news_service.add_or_update_input_news_batch(
            input_news_list=mocked_news
        )
        print(f"Additional input news loaded: {len(input_news)} articles")

        # Test connecting existing news (should be 1 for second run)
        generated_news = await article_generation_service.connect_existing_news(delta=self.delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, (
            f"The testing workflow should add exactly 1 connected news. "
            f"Generated: {len(generated_news)}"
        )

        # Test creating new news (should be 1 for second run)
        generated_news = await article_generation_service.creates_new_news(delta=self.delta)
        verify_generated_news(generated_news)
        assert len(generated_news) == 1, (
            f"Service should generate exactly 1 news article. "
            f"Generated: {len(generated_news)}"
        )

        await session.flush()
        print("Second batch test completed successfully.")


async def run_news_processing_test(commit_transaction: bool = False):
    """Run the complete news processing test suite"""
    test_instance = NewsProcessingTest(commit_transaction=commit_transaction)
    await test_instance.test_parse_news_workflow()


# Pytest integration
@pytest.mark.asyncio
async def test_news_processing_pytest():
    """Pytest-compatible test function"""
    await run_news_processing_test(commit_transaction=False)


def main():
    """CLI entry point for running tests"""
    import argparse

    parser = argparse.ArgumentParser(description="News Processing Test Suite")
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit transaction to database (useful for manual verification)"
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_news_processing_test(commit_transaction=args.commit))
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(exit_code := main())
