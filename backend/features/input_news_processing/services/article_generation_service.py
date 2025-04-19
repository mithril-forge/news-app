from datetime import datetime

from features.api_service.services.topic_service import TopicService


class ArticleGenerationService:
    def __init__(self, session, topic_service: TopicService):
        self.session = session
        self.topic_service = topic_service

    def creates_new_articles(self, from_date: datetime) -> None:
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

    async def get_input_news_from_time(self, from_date: datetime) -> list:
        # Query to get relevant input news
        pass
