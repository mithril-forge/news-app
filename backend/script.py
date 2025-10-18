import asyncio

from dramatiq_tasks import async_generate_article_task

result = asyncio.run(async_generate_article_task([8054, 8031], 10))
