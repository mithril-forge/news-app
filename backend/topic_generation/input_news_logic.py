from datetime import datetime

from topic_generation.input_news_schema import InputNewsMetadata


def parse_news(from_date: datetime, to_date: datetime) -> None:
    # TODO: 1. Calls function to get all the parsed news -> we don't care about return value, the result will be list of pydantic models
    models: list[InputNewsMetadata] = []
    # 2. Push data to the DB -> check is done by source_url -> if same then just updates the article


def creates_new_articles(from_date: datetime) -> None:
    # 1. Query all input news +- 7 days (from_date), join will be done on connected article. They will be 2 inputs:
    #   a) The existing parsed news with connected input news -> for these news also connect input news older than 1 week
    #   b) The rest of news that isn't connected
    #   c) Existing topics and tags
    # TODO: Think if it's good to do it in one query, or as pipeline -> connect -> create new and then connect tags and categories
    # 2. There will be 2 main queries to the AI:
    #   a) Connect input news to existing parsed ones if they match -> adjust content if there is anything important that can be added
    #   b) Create new parsed news if they can connect at least 2 input news (threshold 2, if too low then we can increase)
    #   c) Connect existing tags and the topic -> if tags are not sufficient, then create, but try to use existing ones if possible
    # 3. Output should be as Pydantic model defined in input_news_schema.py -> clearly connect ID of parsed news then content and needed things
    # 4. Saves new/updated parsed news to DB and connect properly the input news
    pass

def clear_old_input_news() -> None:
    # 1. Archive old input news from relational DB to same file dump or data lake. The threshold should be something like 1-2 months.
    pass


