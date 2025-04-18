from datetime import datetime
from typing import Any

from topic_generation.input_news_schema import InputNewsMetadata


def load_testing_input_news_data(test_articles: list[str, Any]) -> list[InputNewsMetadata]:
    # Convert the data back to Pydantic models
    articles = []
    for article_dict in test_articles:
        # Convert string back to datetime
        article_dict["publication_date"] = datetime.fromisoformat(article_dict["publication_date"])

        # Create Pydantic model
        article = InputNewsMetadata(**article_dict)
        articles.append(article)

    return articles