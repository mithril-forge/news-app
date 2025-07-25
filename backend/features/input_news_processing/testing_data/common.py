from typing import Any

from features.input_news_processing.domain.schemas import InputNews
from features.input_news_processing.testing_data.additional_input_news import (
    ADDITIONAL_ARTICLES,
)
from features.input_news_processing.testing_data.initial_input_news import (
    INITIAL_INPUT_ARTICLES,
)


def load_testing_input_news_data(
    test_articles: list[dict[str, Any]],
) -> list[InputNews]:
    # Convert the data back to Pydantic models
    articles = []
    for article_dict in test_articles:
        # Create Pydantic model
        article = InputNews(**article_dict)
        articles.append(article)

    return articles


mock_data = iter(
    [
        load_testing_input_news_data(INITIAL_INPUT_ARTICLES),
        load_testing_input_news_data(ADDITIONAL_ARTICLES),
    ]
)
