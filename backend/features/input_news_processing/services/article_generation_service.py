import json
import os
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

import instructor
from instructor import AsyncInstructor
from pydantic import BaseModel
import google.generativeai as genai

from features.api_service.database.repository import AsyncTagRepository
from features.api_service.services.schemas import TagResponse, TopicResponse
from features.api_service.services.topic_service import TopicService
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsSchema, ConnectionResult

CONNECTION_PROMPT = """
Analýza zpravodajských článků a jejich propojení

V přiložených souborech najdeš 4 typy vstupních dat:

1. INPUT_NEWS:
   - Články scrapované z různých zpravodajských webů
   - Obsahují veškeré původní informace z webů

2. PARSED_NEWS:
   - Naše vytvořené články, které spojují různé zprávy
   - Shrnují a zdůrazňují důležité informace z různých zdrojů

3. TOPICS:
   - Kategorie jednotlivých článků
   - Jsou fixní a neměnné

4. TAGS:
   - Nejsou fixní, lze je přidávat
   - Preferuj používání již existujících tagů
   - Každý článek by měl mít maximálně 3 tagy

TVŮJ ÚKOL:
- Prozkoumej nové články (input_news)
- Zjisti, zda se některé z nich dají propojit s již existujícími články (parsed_news)
- Hledej pouze PŘÍMÉ SHODY - stejná událost/téma/aktualita

VÝSTUP:
- Pro každou nalezenou shodu vytvoř odpověď, která spojí ID relevantních input_news s daným parsed_news
- Můžeš navrhnout vhodné tagy (max. 3, preferuj existující)
- Pokud nové články obsahují zásadní chybějící informace, navrhni úpravy:
  * Doplnění chybějících informací
  * Úprava title a description (pouze při zásadních změnách)
  * Topic se pokus zachovat beze změny
- Pokud nenajdeš žádné shody, potom nevracej nic
"""


class TempFileStorage(BaseModel):
    recent_parsed_news: Path
    topics: Path
    tags: Path
    recent_input_news: Path


class ArticleGenerationService:
    def __init__(self, session):
        self.session = session
        self.topic_service = TopicService(session=session)
        self.input_news_service = InputNewsService(session=session)
        self.tag_repository = AsyncTagRepository(session=session)

    @staticmethod
    def save_pydantic_lists_as_files(tags_list: list[TagResponse], topics_list: list[TopicResponse],
                                     recent_parsed_news: list[ParsedNewsWithInputNews],
                                     recent_input_news: list[InputNewsSchema]):
        paths_mapping: dict[str, Path] = {}
        model_lists = {
            "recent_parsed_news": recent_parsed_news,
            "topics": topics_list,
            "tags": tags_list,
            "recent_input_news": recent_input_news
        }

        for list_name, model_list in model_lists.items():
            data = [model.model_dump_json() for model in model_list]
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.json',
                mode='w+',
                delete=False
            )

            json.dump(data, temp_file, indent=2)
            temp_file.close()

            paths_mapping[list_name] = Path(temp_file.name)

        return TempFileStorage(**paths_mapping)

    async def prepare_gemini_client(self) -> AsyncInstructor:
        gemini_api_key = os.environ["GEMINI_API_KEY"]
        if gemini_api_key is None:
            raise ValueError("You need to provide GEMINI_API_KEY")
        genai.configure(api_key=gemini_api_key)
        client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name="gemini-1.5-flash-002",
            ),
            mode=instructor.Mode.GEMINI_JSON,
            use_async=True  # Ensure async is enabled
        )
        return client

    @staticmethod
    def upload_files_gemini(file_storage: TempFileStorage) -> dict[str, genai.types.File]:
        """Uploads a file synchronously and returns the File object."""
        results: dict[str, genai.types.File] = {}
        for key, file_path in file_storage.model_dump().items():
            if not file_path.exists():
                raise ValueError(f"File path {file_path} not found")
            file_obj = genai.upload_file(path=file_path, display_name=key, mime_type='text/plain')
            print(f"File uploaded successfully: URI = {file_obj.uri}")
            results[key] = file_obj
        return results


    @staticmethod
    async def prepare_gemini_files(file_paths: TempFileStorage) -> list[dict[str, Any]]:
        """

        """
        file_contents = []

        for list_name, model_list in file_paths.model_dump().items():
            # Convert models to JSON
            if hasattr(model_list[0], "model_dump"):  # Pydantic v2
                data = [model.model_dump() for model in model_list]
            else:  # Pydantic v1
                data = [model.dict() for model in model_list]

            # Create file content
            json_content = json.dumps(data, indent=2)

            # Add to file_contents with appropriate MIME type
            file_contents.append({
                "mime_type": "text/plain",
                "data": json_content,  # Encode as bytes
                "name": f"{list_name}.txt"  # Give each file a name
            })
        return file_contents

    async def creates_new_articles(self, timedelta_back: timedelta) -> None:
        recent_input_news = await self.input_news_service.get_input_news_from_time(delta=timedelta_back,
                                                                                   has_parsed_news=False)
        recent_parsed_news = await self.input_news_service.get_parsed_with_input_news(delta=timedelta_back)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = await self.tag_repository.get_all()
        file_storage = self.save_pydantic_lists_as_files(tags_list=existing_tags, topics_list=existing_topics,
                                                         recent_parsed_news=recent_parsed_news,
                                                         recent_input_news=recent_input_news)
        gemini_client = await self.prepare_gemini_client()
        #file_contents = self.prepare_gemini_files(file_paths=file_storage)
        gemini_files = self.upload_files_gemini(file_storage=file_storage)
        contents = [
            CONNECTION_PROMPT
        ]
        contents.extend(gemini_files.values())
        result = await gemini_client.chat.completions.create(response_model=Iterable[ConnectionResult],
                                                             messages=[{"role": "user", "content": contents}])
        print(result)
        # TODO: Fix prompt so it generates proper content, not only summary in content
        # TODO: Fix prompt so it doesn't generate new articles
        # TODO: Add support for gemini-pro
        # TODO: Save the result to DB
        # TODO: Try to add some similar tags to the created one, so we see if the AI matches the existing ones and don't create new ones. It also appends 4 tags instead of 3.
        # TODO: Add query and logic to generate new parsed news
        # TODO: Saves DB
        pass

    async def get_parsed_news(self, from_timedelta: timedelta):
        pass
