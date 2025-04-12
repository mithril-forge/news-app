# TODO: Fix relative imports and place under database
import asyncio
from datetime import datetime
from typing import List, Dict

from sqlmodel.ext.asyncio.session import AsyncSession

from database.engine import create_async_db_and_tables, get_async_session
from database.models import Topic, Tag, ParsedNews
from database.repository import AsyncTopicRepository, AsyncTagRepository, AsyncParsedNewsRepository, \
    AsyncInputNewsRepository


async def create_initial_topics(session: AsyncSession) -> Dict[str, Topic]:
    """Create initial topics if they don't exist."""
    topic_repo = AsyncTopicRepository(session)

    # Define initial topics
    initial_topics = [
        {"name": "Technology", "description": "News about technology, gadgets, and digital trends"},
        {"name": "Politics", "description": "Political news and current affairs"},
        {"name": "Business", "description": "Business, finance, and economic news"},
        {"name": "Science", "description": "Scientific discoveries and research"},
        {"name": "Health", "description": "Health, wellness, and medical news"}
    ]

    # Dictionary to store created topics
    topics_dict = {}

    for topic_data in initial_topics:
        # Check if topic already exists
        existing_topic = await topic_repo.get_by_name(topic_data["name"])
        if not existing_topic:
            # Create new topic
            print(f"Creating topic: {topic_data['name']}")
            topic = await topic_repo.add(topic_data)
            topics_dict[topic.name] = topic
        else:
            print(f"Topic already exists: {topic_data['name']}")
            topics_dict[existing_topic.name] = existing_topic

    return topics_dict


async def create_initial_tags(session: AsyncSession) -> Dict[str, Tag]:
    """Create initial tags if they don't exist."""
    tag_repo = AsyncTagRepository(session)

    # Define initial tags
    initial_tags = [
        "trending", "important", "breaking", "analysis", "opinion",
        "innovation", "research", "policy", "market", "global",
        "local", "health", "environment", "education", "security"
    ]

    # Dictionary to store created tags
    tags_dict = {}

    # Create tags if they don't exist
    for tag_text in initial_tags:
        # Check if tag already exists
        existing_tag = await tag_repo.get_by_text(tag_text)
        if not existing_tag:
            # Create new tag
            print(f"Creating tag: {tag_text}")
            tag = await tag_repo.add({"text": tag_text})
            tags_dict[tag.text] = tag
        else:
            print(f"Tag already exists: {tag_text}")
            tags_dict[existing_tag.text] = existing_tag

    return tags_dict


async def create_sample_news(
        session: AsyncSession,
        topics_dict: Dict[str, Topic],
        tags_dict: Dict[str, Tag]
) -> List[ParsedNews]:
    """Create sample news articles if they don't exist."""
    news_repo = AsyncParsedNewsRepository(session)

    # Define sample news
    sample_news = [
        {
            "title": "New AI breakthrough transforms natural language processing",
            "description": "Researchers have developed a new AI model that significantly improves natural language understanding.",
            "content": "A team of researchers has announced a breakthrough in natural language processing that could revolutionize how computers understand human language. The new model achieves unprecedented accuracy in comprehension tasks...",
            "image_url": "https://example.com/ai-breakthrough.jpg",
            "topic": "Technology",
            "tags": ["innovation", "research", "trending"]
        },
        {
            "title": "Global climate agreement reaches new milestone",
            "description": "World leaders have agreed on ambitious new climate targets at the annual summit.",
            "content": "In a historic development, representatives from 195 countries have reached consensus on a new framework to address climate change. The agreement includes binding targets for emission reductions...",
            "image_url": "https://example.com/climate-summit.jpg",
            "topic": "Politics",
            "tags": ["global", "environment", "important"]
        },
        {
            "title": "Stock markets rally after central bank announcement",
            "description": "Global markets responded positively to new monetary policy measures.",
            "content": "Stock markets worldwide surged today following an announcement from major central banks about coordinated monetary policy actions. The Dow Jones Industrial Average climbed 2.3% while European markets...",
            "image_url": "https://example.com/stock-market.jpg",
            "topic": "Business",
            "tags": ["market", "global", "breaking"]
        },
        {
            "title": "New vaccine shows promise against multiple viral threats",
            "description": "Scientists have developed a versatile vaccine platform that could help fight multiple viruses.",
            "content": "A groundbreaking vaccine technology has demonstrated effectiveness against multiple viral pathogens in early-stage clinical trials. The platform uses novel mRNA delivery mechanisms to train the immune system...",
            "image_url": "https://example.com/vaccine-research.jpg",
            "topic": "Health",
            "tags": ["health", "research", "innovation"]
        }
    ]

    created_news = []

    # Create news if they don't exist
    for news_data in sample_news:
        # Check if news already exists
        existing_news = await news_repo.get_by_title(news_data["title"])
        if not existing_news:
            # Get topic
            topic = topics_dict.get(news_data["topic"])
            if not topic:
                print(f"Topic not found: {news_data['topic']}, skipping news")
                continue

            # Prepare news data
            parsed_news_data = {
                "title": news_data["title"],
                "description": news_data["description"],
                "content": news_data["content"],
                "image_url": news_data["image_url"],
                "topic_id": topic.id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Get tag texts
            tag_texts = [tag_text for tag_text in news_data["tags"] if tag_text in tags_dict]

            # Create news with tags
            print(f"Creating news: {news_data['title']}")
            news = await news_repo.prepare_with_tags(parsed_news_data, tag_texts)
            created_news.append(news)
        else:
            print(f"News already exists: {news_data['title']}")
            created_news.append(existing_news)

    return created_news


async def create_sample_input_news(
        session: AsyncSession,
        parsed_news: List[ParsedNews]
) -> None:
    """Create sample input news records if they don't exist."""
    input_repo = AsyncInputNewsRepository(session)

    # Define sample input news
    sample_inputs = [
        {
            "source": "web_scraper",
            "description": "Scraped from Technology News Website",
            "raw_metadata": {
                "url": "https://technews.example.com/ai-breakthrough",
                "scrape_time": "2023-03-15T14:30:00Z",
                "category": "artificial-intelligence"
            },
            "parsed_news_id": parsed_news[0].id if len(parsed_news) > 0 else None
        },
        {
            "source": "rss_feed",
            "description": "From Global Politics RSS Feed",
            "raw_metadata": {
                "feed_url": "https://politics.example.com/rss",
                "published_date": "2023-03-14T09:15:00Z",
                "author": "John Smith"
            },
            "parsed_news_id": parsed_news[1].id if len(parsed_news) > 1 else None
        },
        {
            "source": "api",
            "description": "Retrieved from Financial News API",
            "raw_metadata": {
                "api_endpoint": "https://api.financenews.example.com/v1/articles",
                "request_timestamp": "2023-03-15T10:45:00Z",
                "api_version": "1.2.3"
            },
            "parsed_news_id": parsed_news[2].id if len(parsed_news) > 2 else None
        },
        {
            "source": "email_submission",
            "description": "Submitted via email alert system",
            "raw_metadata": {
                "email_id": "news-alerts@medicalnews.example.com",
                "received_timestamp": "2023-03-16T08:20:00Z",
                "priority": "high"
            },
            "parsed_news_id": None  # Unprocessed
        }
    ]

    # Create input news if they don't exist
    for i, input_data in enumerate(sample_inputs):
        # Check if we're looking for an already processed entry
        if input_data.get("parsed_news_id") is not None:
            # Check if there's already an input news with this parsed_news ID
            from sqlmodel import select
            from database.models import InputNews

            statement = select(InputNews).where(
                InputNews.parsed_news == input_data['parsed_news_id'])
            result = await session.execute(statement)
            existing = result.first()
            if existing:
                print(
                    f"Input news for parsed_news_id {input_data['parsed_news_id']} already exists")
                continue

        # Otherwise create a new input news entry
        print(f"Creating input news: {input_data['description']}")
        input_news_data = {
            "source": input_data["source"],
            "description": input_data["description"],
            "raw_metadata": input_data["raw_metadata"],
            "received_at": datetime.utcnow(),
        }

        # Set processed_at and parsed_news if this input is already processed
        if input_data.get("parsed_news_id"):
            input_news_data["processed_at"] = datetime.utcnow()
            input_news_data["parsed_news"] = input_data["parsed_news_id"]

        await input_repo.add(input_news_data)

async def init_data():
    """Initialize the database with sample data."""
    print("Creating database and tables if they don't exist...")
    await create_async_db_and_tables()

    # Get a session
    async for session in get_async_session():
        print("Creating initial data...")

        # Create topics
        topics = await create_initial_topics(session)
        print(f"Created/found {len(topics)} topics")

        # Create tags
        tags = await create_initial_tags(session)
        print(f"Created/found {len(tags)} tags")

        # Create sample news
        news = await create_sample_news(session, topics, tags)
        print(f"Created/found {len(news)} news articles")

        # Create sample input news
        await create_sample_input_news(session, news)
        print("Created sample input news")

        await session.commit()
        print("Initial data creation complete!")
        break  # Exit after one session



if __name__ == "__main__":
    asyncio.run(init_data())