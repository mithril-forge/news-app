from datetime import datetime
from typing import Any

from topic_generation.input_news_schema import InputNewsSchema


def load_testing_input_news_data(test_articles: list[str, Any]) -> list[InputNewsSchema]:
    # Convert the data back to Pydantic models
    articles = []
    for article_dict in test_articles:

        # Create Pydantic model
        article = InputNewsSchema(**article_dict)
        articles.append(article)

    return articles