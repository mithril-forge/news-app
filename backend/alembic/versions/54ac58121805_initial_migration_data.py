"""initial migration data

Revision ID: 54ac58121805
Revises: 457bd7bd915a
Create Date: 2025-04-09 15:43:41.793850

"""
import json
from typing import Sequence, Union
from datetime import datetime
from datetime import timedelta
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '54ac58121805'
down_revision: Union[str, None] = '457bd7bd915a'
branch_labels: Union[str, Sequence[str], None] = ('dev',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    meta = sa.MetaData()

    # Reflexe nebo explicitní definice tabulek
    topics_table = sa.Table('topics', meta, autoload_with=bind)
    tags_table = sa.Table('tags', meta, autoload_with=bind)
    parsed_news_table = sa.Table('parsed_news', meta, autoload_with=bind)
    input_news_table = sa.Table('input_news', meta, autoload_with=bind)
    parsed_news_tag_link_table = sa.Table('parsed_news_tag_link', meta, autoload_with=bind)

    print("Inserting initial topics...")
    op.bulk_insert(topics_table,
                   [
                       {'name': 'Politika', 'description': 'Zprávy z domácí i zahraniční politiky.'},
                       {'name': 'Sport', 'description': 'Aktuality ze světa sportu.'},
                       {'name': 'Technologie', 'description': 'Novinky z oblasti technologií, vědy a IT.'},
                       {'name': 'Kultura', 'description': 'Filmy, hudba, divadlo, umění.'},
                       {'name': 'Ekonomika', 'description': 'Byznys, finance, trhy.'},
                       {'name': 'Věda', 'description': 'Objevy, výzkum, vesmír.'},
                       {'name': 'Cestování', 'description': 'Tipy na výlety, destinace.'},
                       {'name': 'Zdraví', 'description': 'Životní styl, medicína.'},
                   ]
                   )

    print("Inserting initial tags...")
    op.bulk_insert(tags_table,
                   [
                       {'text': 'Volby'},
                       {'text': 'Fotbal'},
                       {'text': 'AI'},
                       {'text': 'Domácí'},
                       {'text': 'Hardware'},
                       {'text': 'Zahraniční'},
                       {'text': 'Film'},
                       {'text': 'Hudba'},
                       {'text': 'Recenze'},
                       {'text': 'Startup'},
                       {'text': 'Výzkum'},
                       {'text': 'Hory'},
                       {'text': 'Dieta'},
                       {'text': 'EU'},
                       {'text': 'ČR'},
                       {'text': 'Ekonomika'},  # Added tag
                       {'text': 'Finance'},  # Added tag
                       {'text': 'Cestování'},  # Added tag
                       {'text': 'Zdraví'},  # Added tag
                       {'text': 'Politika'},  # Added tag
                       {'text': 'Technologie'},  # Added tag
                       {'text': 'Software'},  # Added tag
                       {'text': 'Kultura'}
                   ]
                   )

    # Získání ID vložených témat a štítků (jednodušší přístup než RETURNING)
    print("Fetching IDs for topics and tags...")
    res_topics = bind.execute(sa.select(topics_table.c.id, topics_table.c.name)).mappings().all()
    topic_id_map = {r['name']: r['id'] for r in res_topics}

    res_tags = bind.execute(sa.select(tags_table.c.id, tags_table.c.text)).mappings().all()
    tag_id_map = {r['text']: r['id'] for r in res_tags}

    # Basic checks for added items
    required_topics = ['Politika', 'Technologie', 'Ekonomika', 'Kultura', 'Sport', 'Věda', 'Cestování', 'Zdraví']
    required_tags = ['Volby', 'Domácí', 'AI', 'Hardware', 'Film', 'Startup', 'Ekonomika', 'Finance', 'Cestování',
                     'Zdraví', 'Politika', 'Technologie', 'Software']

    for topic in required_topics:
        if topic not in topic_id_map:
            raise Exception(f"Failed to load ID for initial topic '{topic}'.")
    for tag in required_tags:
        if tag not in tag_id_map:
            raise Exception(f"Failed to load ID for initial tag '{tag}'.")

    print("Inserting initial news (ParsedNews)...")
    now = datetime.utcnow()
    news_data = [
        {
            'title': 'Výsledky voleb přinesly překvapení',
            'description': 'Krátký souhrn volebních výsledků v ČR.',
            'content': 'Podrobný obsah článku o volebních výsledcích, analýzy, komentáře...',
            'image_url': 'https://via.placeholder.com/150/FF0000/FFFFFF?text=VolbyCR',
            'created_at': now - timedelta(days=1),
            'updated_at': now - timedelta(days=1),
            'topic_id': topic_id_map['Politika']
        },
        {
            'title': 'Nový AI model od Google mění pravidla hry',
            'description': 'Google představil pokročilý model umělé inteligence Gemini Pro 2.0.',
            'content': 'Technické detaily a možnosti nového AI modelu, srovnání s konkurencí...',
            'image_url': 'https://via.placeholder.com/150/0000FF/FFFFFF?text=AI_Google',
            'created_at': now - timedelta(hours=5),
            'updated_at': now - timedelta(hours=4),
            'topic_id': topic_id_map['Technologie']
        },
        {
            'title': 'Mistrovství světa ve fotbale: Finále',
            'description': 'Reportáž z napínavého finálového utkání mezi Brazílií a Německem.',
            'content': 'Průběh zápasu, klíčové momenty, rozhovory s hráči...',
            'image_url': 'https://via.placeholder.com/150/00FF00/000000?text=FotbalWC',
            'created_at': now - timedelta(days=3),
            'updated_at': now - timedelta(days=3, hours=2),
            'topic_id': topic_id_map['Sport']
        },
        {
            'title': 'Premiéra nového českého filmu "Osamělí běžci"',
            'description': 'Recenze očekávaného snímku od režiséra Jana Nováka.',
            'content': 'Hodnocení filmu, hereckých výkonů, kamery a hudby...',
            'image_url': 'https://via.placeholder.com/150/FFFF00/000000?text=FilmCZ',
            'created_at': now - timedelta(days=2),
            'updated_at': now - timedelta(days=2),
            'topic_id': topic_id_map['Kultura']
        },
        {
            'title': 'ČNB překvapivě zvýšila úrokové sazby o 0.5 procentního bodu',
            'description': 'Reakce finančních trhů na nečekaný krok centrální banky.',
            'content': 'Důvody rozhodnutí ČNB, dopady na hypotéky a ekonomiku...',
            'image_url': 'https://via.placeholder.com/150/FF00FF/FFFFFF?text=CNB_Sazby',
            'created_at': now - timedelta(hours=12),
            'updated_at': now - timedelta(hours=11),
            'topic_id': topic_id_map['Ekonomika']
        },
        {
            'title': 'Objev nové exoplanety v obyvatelné zóně',
            'description': 'Vědci oznámili nález planety Kepler-452g podobné Zemi u vzdálené hvězdy.',
            'content': 'Parametry planety, podmínky pro život, další výzkum...',
            'image_url': 'https://via.placeholder.com/150/00FFFF/000000?text=Exoplaneta',
            'created_at': now - timedelta(days=5),
            'updated_at': now - timedelta(days=4),
            'topic_id': topic_id_map['Věda']
        },
        {
            'title': 'Tipy na víkendový výlet do Českého Švýcarska',
            'description': 'Kam vyrazit za krásnými výhledy a unikátními skalními útvary.',
            'content': 'Popis tras, zajímavá místa, doporučení na ubytování...',
            'image_url': 'https://via.placeholder.com/150/FFA500/000000?text=CeskeSvyc',
            'created_at': now - timedelta(days=6),
            'updated_at': now - timedelta(days=6),
            'topic_id': topic_id_map['Cestování']
        },
        {
            'title': 'Studie potvrzuje výhody středomořské diety pro prevenci kardiovaskulárních chorob',
            'description': 'Rozsáhlý výzkum ukázal, jaký vliv má strava na zdraví srdce a cév.',
            'content': 'Detailní výsledky studie, doporučení pro jídelníček...',
            'image_url': 'https://via.placeholder.com/150/800080/FFFFFF?text=DietaZdravi',
            'created_at': now - timedelta(days=7),
            'updated_at': now - timedelta(days=7, hours=1),
            'topic_id': topic_id_map['Zdraví']
        },
        {
            'title': 'Jednání vlády o reformě důchodového systému',
            'description': 'Ministři projednávali klíčové body navrhované důchodové reformy.',
            'content': 'Hlavní návrhy, sporné body, očekávaný další postup...',
            'image_url': 'https://via.placeholder.com/150/FFC0CB/000000?text=VladaDuchody',
            'created_at': now - timedelta(hours=3),
            'updated_at': now - timedelta(hours=2),
            'topic_id': topic_id_map['Politika']
        },
        {
            'title': 'Český startup \'DataFriends\' získal investici 5 milionů EUR',
            'description': 'Brněnská technologická firma zaměřená na analýzu dat uspěla u zahraničních investorů.',
            'content': 'Podrobnosti o investici, plány firmy na expanzi, technologie...',
            'image_url': 'https://via.placeholder.com/150/008000/FFFFFF?text=StartupData',
            'created_at': now - timedelta(hours=8),
            'updated_at': now - timedelta(hours=8),
            'topic_id': topic_id_map['Technologie']
        },
        {
            'title': 'Nové album kapely \'Naděje\' trhá rekordy',
            'description': 'Recenze a první ohlasy na dlouho očekávanou desku.',
            'content': 'Rozbor jednotlivých skladeb, srovnání s předchozí tvorbou...',
            'image_url': 'https://via.placeholder.com/150/808080/FFFFFF?text=HudbaNadeje',
            'created_at': now - timedelta(days=4),
            'updated_at': now - timedelta(days=4),
            'topic_id': topic_id_map['Kultura']
        },
        {
            'title': 'Jak vybrat správný hardware pro AI vývoj',
            'description': 'Průvodce výběrem grafických karet a procesorů pro trénování modelů.',
            'content': 'Srovnání Nvidia vs AMD, doporučené konfigurace, cloudové alternativy...',
            'image_url': 'https://via.placeholder.com/150/A52A2A/FFFFFF?text=AIHardware',
            'created_at': now - timedelta(hours=6),
            'updated_at': now - timedelta(hours=6),
            'topic_id': topic_id_map['Technologie']
        }
    ]
    op.bulk_insert(parsed_news_table, news_data)

    # Získání ID vložených zpráv
    print("Fetching IDs for inserted news...")
    res_news = bind.execute(sa.select(parsed_news_table.c.id, parsed_news_table.c.title)).mappings().all()
    news_id_map = {r['title']: r['id'] for r in res_news}

    # Check some new news items
    required_news_titles = [
        'Výsledky voleb přinesly překvapení', 'Nový AI model od Google mění pravidla hry',
        'Mistrovství světa ve fotbale: Finále', 'ČNB překvapivě zvýšila úrokové sazby o 0.5 procentního bodu',
        'Český startup \'DataFriends\' získal investici 5 milionů EUR', 'Jak vybrat správný hardware pro AI vývoj'
    ]
    for title in required_news_titles:
        if title not in news_id_map:
            raise Exception(f"Failed to load ID for initial news item '{title}'.")

    # Map news IDs to variables for clarity
    news_id_volby = news_id_map['Výsledky voleb přinesly překvapení']
    news_id_ai = news_id_map['Nový AI model od Google mění pravidla hry']
    news_id_fotbal = news_id_map['Mistrovství světa ve fotbale: Finále']
    news_id_film = news_id_map['Premiéra nového českého filmu "Osamělí běžci"']
    news_id_cnb = news_id_map['ČNB překvapivě zvýšila úrokové sazby o 0.5 procentního bodu']
    news_id_planeta = news_id_map['Objev nové exoplanety v obyvatelné zóně']
    news_id_hory = news_id_map['Tipy na víkendový výlet do Českého Švýcarska']
    news_id_dieta = news_id_map['Studie potvrzuje výhody středomořské diety pro prevenci kardiovaskulárních chorob']
    news_id_vlada = news_id_map['Jednání vlády o reformě důchodového systému']
    news_id_startup = news_id_map['Český startup \'DataFriends\' získal investici 5 milionů EUR']
    news_id_hudba = news_id_map['Nové album kapely \'Naděje\' trhá rekordy']
    news_id_ai_hw = news_id_map['Jak vybrat správný hardware pro AI vývoj']

    print("Inserting links between news and tags...")
    op.bulk_insert(parsed_news_tag_link_table,
                   [
                       # Volby
                       {'news_item_id': news_id_volby, 'tag_id': tag_id_map['Volby']},
                       {'news_item_id': news_id_volby, 'tag_id': tag_id_map['Domácí']},
                       {'news_item_id': news_id_volby, 'tag_id': tag_id_map['Politika']},
                       {'news_item_id': news_id_volby, 'tag_id': tag_id_map['ČR']},
                       # AI Google
                       {'news_item_id': news_id_ai, 'tag_id': tag_id_map['AI']},
                       {'news_item_id': news_id_ai, 'tag_id': tag_id_map['Technologie']},
                       {'news_item_id': news_id_ai, 'tag_id': tag_id_map['Software']},
                       # Fotbal
                       {'news_item_id': news_id_fotbal, 'tag_id': tag_id_map['Fotbal']},
                       {'news_item_id': news_id_fotbal, 'tag_id': tag_id_map['Zahraniční']},
                       # Film
                       {'news_item_id': news_id_film, 'tag_id': tag_id_map['Film']},
                       {'news_item_id': news_id_film, 'tag_id': tag_id_map['Recenze']},
                       {'news_item_id': news_id_film, 'tag_id': tag_id_map['Domácí']},
                       {'news_item_id': news_id_film, 'tag_id': tag_id_map['Kultura']},  # Tag 'Kultura' needed
                       # ČNB
                       {'news_item_id': news_id_cnb, 'tag_id': tag_id_map['Ekonomika']},
                       {'news_item_id': news_id_cnb, 'tag_id': tag_id_map['ČR']},
                       {'news_item_id': news_id_cnb, 'tag_id': tag_id_map['Finance']},
                       # Planeta
                       {'news_item_id': news_id_planeta, 'tag_id': tag_id_map['Výzkum']},
                       {'news_item_id': news_id_planeta, 'tag_id': tag_id_map['Zahraniční']},
                       # Hory
                       {'news_item_id': news_id_hory, 'tag_id': tag_id_map['Cestování']},
                       {'news_item_id': news_id_hory, 'tag_id': tag_id_map['Hory']},
                       {'news_item_id': news_id_hory, 'tag_id': tag_id_map['Domácí']},
                       # Dieta
                       {'news_item_id': news_id_dieta, 'tag_id': tag_id_map['Zdraví']},
                       {'news_item_id': news_id_dieta, 'tag_id': tag_id_map['Dieta']},
                       {'news_item_id': news_id_dieta, 'tag_id': tag_id_map['Výzkum']},
                       # Vlada
                       {'news_item_id': news_id_vlada, 'tag_id': tag_id_map['Politika']},
                       {'news_item_id': news_id_vlada, 'tag_id': tag_id_map['Domácí']},
                       {'news_item_id': news_id_vlada, 'tag_id': tag_id_map['ČR']},
                       # Startup
                       {'news_item_id': news_id_startup, 'tag_id': tag_id_map['Technologie']},
                       {'news_item_id': news_id_startup, 'tag_id': tag_id_map['Startup']},
                       {'news_item_id': news_id_startup, 'tag_id': tag_id_map['Ekonomika']},
                       # Hudba
                       {'news_item_id': news_id_hudba, 'tag_id': tag_id_map['Hudba']},
                       {'news_item_id': news_id_hudba, 'tag_id': tag_id_map['Kultura']},
                       {'news_item_id': news_id_hudba, 'tag_id': tag_id_map['Recenze']},
                       # AI Hardware
                       {'news_item_id': news_id_ai_hw, 'tag_id': tag_id_map['AI']},
                       {'news_item_id': news_id_ai_hw, 'tag_id': tag_id_map['Hardware']},
                       {'news_item_id': news_id_ai_hw, 'tag_id': tag_id_map['Technologie']},
                   ]
                   )

    print("Inserting initial input data (InputNews)...")
    op.bulk_insert(input_news_table,
                   [
                       # Original + Added
                       {
                           'source': 'ČT24 RSS',
                           'description': 'Položka z RSS feedu ČT24 týkající se voleb.',
                           'raw_metadata': json.dumps(
                               {'url': 'http://ct24.ceskatelevize.cz/volby-item-123', 'feed_name': 'Domácí'}),
                           'parsed_news': news_id_volby,
                           'received_at': now - timedelta(days=1, hours=1),
                           'processed_at': now - timedelta(days=1)
                       },
                       {
                           'source': 'API Google News',
                           'description': 'Položka z API o novém AI modelu Google.',
                           'raw_metadata': json.dumps({'article_id': 'google-ai-gemini-pro-2', 'source_region': 'US'}),
                           'parsed_news': news_id_ai,
                           'received_at': now - timedelta(hours=6),
                           'processed_at': now - timedelta(hours=4)
                       },
                       {
                           'source': 'Nezpracovaný Webhook',
                           'description': 'Nějaká data z webhooku, zatím nezpracovaná.',
                           'raw_metadata': json.dumps({'payload_id': 'wh-abc-1', 'sender': 'external-system-A'}),
                           'parsed_news': None,
                           'received_at': now - timedelta(minutes=30),
                           'processed_at': None
                       },
                       {
                           'source': 'Sport.cz API',
                           'description': 'Výsledek finále MS ve fotbale: Brazílie 2:3 Německo.',
                           'raw_metadata': json.dumps({'match_id': 'WC2025-FIN', 'score': '2-3', 'winner': 'GER'}),
                           'parsed_news': news_id_fotbal,
                           'received_at': now - timedelta(days=3, hours=3),
                           'processed_at': now - timedelta(days=3, hours=2)
                       },
                       {
                           'source': 'CSFD Web Scraper',
                           'description': 'Info o premiéře filmu Osamělí běžci.',
                           'raw_metadata': json.dumps(
                               {'url': 'https://www.csfd.cz/film/osameli-bezci/', 'rating': '81%',
                                'director': 'Jan Novák'}),
                           'parsed_news': news_id_film,
                           'received_at': now - timedelta(days=2, hours=1),
                           'processed_at': now - timedelta(days=2)
                       },
                       {
                           'source': 'Reuters Feed',
                           'description': 'Reakce finančních trhů na zvýšení sazeb ČNB.',
                           'raw_metadata': json.dumps(
                               {'feed_id': 'reuters-econ-cz-rates', 'timestamp': str(now - timedelta(hours=12)),
                                'currency': 'CZK'}),
                           'parsed_news': news_id_cnb,
                           'received_at': now - timedelta(hours=13),
                           'processed_at': now - timedelta(hours=11)
                       },
                       {
                           'source': 'NASA Press Release Feed',
                           'description': 'Objev exoplanety Kepler-452g.',
                           'raw_metadata': json.dumps(
                               {'source_url': 'nasa.gov/pr-2025-kepler452g', 'telescope': 'Kepler',
                                'discovery_date': str(now.date() - timedelta(days=5))}),
                           'parsed_news': news_id_planeta,
                           'received_at': now - timedelta(days=5, hours=2),
                           'processed_at': now - timedelta(days=4)
                       },
                       {
                           'source': 'Nezpracovaný Email',
                           'description': 'Tip na článek o Českém Švýcarsku od uživatele',
                           'raw_metadata': json.dumps(
                               {'subject': 'Tip na vylet: Ceske Svycarsko', 'sender': 'franta.vyletnik@example.com',
                                'received_time': str(now - timedelta(days=6, hours=4))}),
                           'parsed_news': None,  # Bude propojeno později
                           'received_at': now - timedelta(days=6, hours=4),
                           'processed_at': None
                       },
                       {
                           'source': 'PubMed API',
                           'description': 'Zdravotní studie o středomořské dietě.',
                           'raw_metadata': json.dumps(
                               {'doi': '10.1234/j.health.2025.01.005', 'journal': 'Medical Journal of Cardiology',
                                'pmid': '12345678'}),
                           'parsed_news': news_id_dieta,
                           'received_at': now - timedelta(days=7, hours=2),
                           'processed_at': now - timedelta(days=7, hours=1)
                       },
                       {
                           'source': 'Vládní Portál API',
                           'description': 'Informace o jednání vlády k důchodům.',
                           'raw_metadata': json.dumps(
                               {'meeting_id': 'vlada-2025-04-08-duchody', 'topic': 'Pension Reform Proposal'}),
                           'parsed_news': news_id_vlada,
                           'received_at': now - timedelta(hours=4),
                           'processed_at': now - timedelta(hours=2)
                       },
                       {
                           'source': 'TechCrunch RSS Feed',
                           'description': 'Český startup DataFriends získal seed investici.',
                           'raw_metadata': json.dumps(
                               {'url': 'techcrunch.com/cz-datafriends-seed', 'author': 'Ingrid Lunden',
                                'category': 'Startups'}),
                           'parsed_news': news_id_startup,
                           'received_at': now - timedelta(hours=9),
                           'processed_at': now - timedelta(hours=8)
                       },
                       {
                           'source': 'Spotify API',
                           'description': 'Nové album od Naděje.',
                           'raw_metadata': json.dumps(
                               {'artist_id': 'spotify:artist:123', 'album_id': 'spotify:album:456',
                                'release_date': str(now.date() - timedelta(days=4))}),
                           'parsed_news': news_id_hudba,
                           'received_at': now - timedelta(days=4, hours=1),
                           'processed_at': now - timedelta(days=4)
                       },
                       {
                           'source': 'Hardware Blog Post',
                           'description': 'Článek o výběru HW pro AI.',
                           'raw_metadata': json.dumps(
                               {'url': 'hardwareblog.com/ai-hardware-guide', 'author': 'TechGuru'}),
                           'parsed_news': news_id_ai_hw,
                           'received_at': now - timedelta(hours=7),
                           'processed_at': now - timedelta(hours=6)
                       },
                       {
                           'source': 'Další Webhook Událost',
                           'description': 'Jiná nezpracovaná data z jiného systému.',
                           'raw_metadata': json.dumps({'event_type': 'item_updated', 'item_id': 'xyz987',
                                                       'timestamp': str(now - timedelta(minutes=5))}),
                           'parsed_news': None,
                           'received_at': now - timedelta(minutes=5),
                           'processed_at': None
                       }
                   ]
                   )

    print("All initial data inserted.")


def downgrade() -> None:
    bind = op.get_bind()

    # Updated lists to include all seeded items for deletion
    input_sources_to_delete = [
        "'ČT24 RSS'", "'API Google News'", "'Nezpracovaný Webhook'", "'Sport.cz API'",
        "'CSFD Web Scraper'", "'Reuters Feed'", "'NASA Press Release Feed'",
        "'Nezpracovaný Email'", "'PubMed API'", "'Vládní Portál API'",
        "'TechCrunch RSS Feed'", "'Spotify API'", "'Hardware Blog Post'",
        "'Další Webhook Událost'"
    ]
    news_titles_to_delete = [
        "'Výsledky voleb přinesly překvapení'", "'Nový AI model od Google mění pravidla hry'",
        "'Mistrovství světa ve fotbale: Finále'", "'Premiéra nového českého filmu \"Osamělí běžci\"'",  # Escaped quote
        "'ČNB překvapivě zvýšila úrokové sazby o 0.5 procentního bodu'",
        "'Objev nové exoplanety v obyvatelné zóně'", "'Tipy na víkendový výlet do Českého Švýcarska'",
        "'Studie potvrzuje výhody středomořské diety pro prevenci kardiovaskulárních chorob'",
        "'Jednání vlády o reformě důchodového systému'",
        "'Český startup \'DataFriends\' získal investici 5 milionů EUR'",  # Already escaped
        "'Nové album kapely \'Naděje\' trhá rekordy'",  # Already escaped
        "'Jak vybrat správný hardware pro AI vývoj'"
    ]
    tag_texts_to_delete = [
        "'Volby'", "'Fotbal'", "'AI'", "'Domácí'", "'Hardware'", "'Zahraniční'",
        "'Film'", "'Hudba'", "'Recenze'", "'Startup'", "'Výzkum'", "'Hory'",
        "'Dieta'", "'EU'", "'ČR'", "'Ekonomika'", "'Finance'", "'Cestování'",
        "'Zdraví'", "'Politika'", "'Technologie'", "'Software'", "'Kultura'",  # Added Kultura
        "'Věda'", "'Byznys'"  # Added Věda, Byznys
    ]
    # Combine original and added topics, ensure unique names if necessary
    topic_names_to_delete = [
        "'Politika'", "'Sport'", "'Technologie'", "'Kultura'", "'Ekonomika'",
        "'Věda'", "'Cestování'", "'Zdraví'"
    ]

    # Mazání v opačném pořadí kvůli foreign keys, začneme vazební tabulkou a input_news
    print("Removing links between news and tags...")
    # Získání ID všech zpráv určených k smazání
    # Handle potential quote issues in titles for the SQL IN clause
    safe_news_titles_sql = ", ".join(news_titles_to_delete)
    news_ids_res = bind.execute(
        sa.text(f"SELECT id FROM parsed_news WHERE title IN ({safe_news_titles_sql})")).fetchall()
    news_ids_to_delete = [str(row[0]) for row in news_ids_res]
    if news_ids_to_delete:
        op.execute(f"DELETE FROM parsed_news_tag_link WHERE news_item_id IN ({','.join(news_ids_to_delete)})")

    print("Removing initial input data (InputNews)...")
    safe_input_sources_sql = ", ".join(input_sources_to_delete)
    op.execute(f"DELETE FROM input_news WHERE source IN ({safe_input_sources_sql})")

    print("Removing initial news (ParsedNews)...")
    op.execute(f"DELETE FROM parsed_news WHERE title IN ({safe_news_titles_sql})")  # Use safe list from above

    print("Removing initial tags...")
    safe_tag_texts_sql = ", ".join(tag_texts_to_delete)
    op.execute(f"DELETE FROM tags WHERE text IN ({safe_tag_texts_sql})")

    print("Removing initial topics...")
    safe_topic_names_sql = ", ".join(topic_names_to_delete)
    op.execute(f"DELETE FROM topics WHERE name IN ({safe_topic_names_sql})")

    print("All initial data removed.")
