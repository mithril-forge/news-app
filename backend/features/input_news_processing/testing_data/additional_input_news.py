from datetime import datetime

from features.input_news_processing.testing_data.common_testing_data import sources

ADDITIONAL_ARTICLES = [
    {
        "tags": [
            "elektromobilita",
            "automobilový průmysl",
            "Hyundai",
            "Ostrava",
            "investice",
        ],
        "category": "Ekonomika",
        "publication_date": datetime(2024, 10, 6, 14, 15),
        "author": "Radek Černý",
        "source_site": sources[1]["name"],
        "source_url": f"{sources[1]['domain']}/ekonomika/hyundai-nova-tovarna-ostrava-elektromobily",
        "content": """Jihokorejská automobilka Hyundai dnes oznámila, že investuje 20 miliard korun do výstavby nové továrny na výrobu elektromobilů v průmyslové zóně nedaleko Ostravy. Podle analýzy ekonomických dopadů by tato investice mohla zvýšit HDP Moravskoslezského kraje až o 2 %.

"Jedná se o strategickou investici nejen pro náš region, ale pro celou Českou republiku," uvedl premiér po jednání s představiteli automobilky. "Podporuje náš cíl transformovat automobilový průmysl směrem k elektromobilitě."

Odboráři z automobilového průmyslu investici vítají, ale upozorňují, že výroba elektromobilů vyžaduje méně pracovníků než tradiční automobilová výroba. "Budeme jednat s vedením firmy o podmínkách zaměstnávání a rekvalifikačních programech," sdělil předseda odborového svazu KOVO.

Stavební práce by měly začít už příští rok v červnu a první elektromobily by měly z továrny vyjet na jaře 2026. Podle zástupců Hyundai bude nový závod využívat nejvyšší stupeň automatizace a robotizace, což umožní vyrábět až 300 000 vozů ročně.

Zajímavostí je, že nová továrna bude využívat převážně obnovitelné zdroje energie, včetně rozsáhlé solární elektrárny na střechách výrobních hal. Hyundai se zavázal, že provoz továrny bude do roku 2030 uhlíkově neutrální.""",
        "title": "Továrna Hyundai v Ostravě zvýší HDP kraje o 2 procenta, říká analýza",
        "summary": "Investice automobilky Hyundai do nové továrny na výrobu elektromobilů v Ostravě má podle ekonomické analýzy zvýšit HDP Moravskoslezského kraje o 2 procenta. Továrna bude využívat vysoký stupeň automatizace a převážně obnovitelné zdroje energie.",
    },
    {
        "tags": ["sport", "fotbal", "EURO 2024", "česká reprezentace", "Patrik Schick"],
        "category": "Sport",
        "publication_date": datetime(2024, 11, 25, 20, 45),
        "author": "Martin Kučera",
        "source_site": sources[0]["name"],
        "source_url": f"{sources[0]['domain']}/sport/fotbal-cesko-postup-euro-2024",
        "content": """Česká fotbalová reprezentace se po vítězství 3:0 nad Moldavskem definitivně kvalifikovala na EURO 2024. Svěřenci trenéra Ivana Haška navázali na úspěšný zápas s Polskem a potvrdili vzestupnou formu.

Hattrickem se blýskl útočník Patrik Schick, který se vrátil po zranění a potvrdil, že je klíčovým hráčem národního týmu. "Po tom vítězství nad Polskem jsme cítili, že máme šanci postoupit přímo. Dnešní výkon byl týmový a jsem rád, že jsem mohl pomoci góly," řekl Schick po zápase.

Česká reprezentace obsadila ve své kvalifikační skupině druhé místo za Albánií, která překvapivě skupinu vyhrála. Na Euru 2024, které se bude konat v Německu, budou Češi nasazeni až do čtvrtého výkonnostního koše, což znamená, že v základní skupině narazí na minimálně dva silné soupeře.

"Teď se musíme dobře připravit. Na Euru nebudeme patřit mezi favority, ale už jsme několikrát ukázali, že umíme překvapit," uvedl trenér Hašek, který převzal reprezentaci v nelehké situaci po neúspěšném vstupu do kvalifikace.

Závěrečný turnaj EURO 2024 se bude hrát od 14. června do 14. července příštího roku. Los základních skupin proběhne 2. prosince v Hamburku.""",
        "title": "Čeští fotbalisté se kvalifikovali na EURO 2024, Schick zaznamenal hattrick",
        "summary": "Česká fotbalová reprezentace si po vítězství 3:0 nad Moldavskem zajistila postup na EURO 2024. Hattrick vstřelil Patrik Schick. Češi skončili ve své kvalifikační skupině na druhém místě za Albánií.",
    },
    # 3. Random article about a different topic - Tech startup
    {
        "tags": [
            "technologie",
            "startup",
            "umělá inteligence",
            "financování",
            "investice",
        ],
        "category": "Technologie",
        "publication_date": datetime(2024, 10, 12, 9, 30),
        "author": "Jan Novotný",
        "source_site": sources[2]["name"],
        "source_url": f"{sources[2]['domain']}/technologie/cesky-startup-ai-financovani",
        "content": """Český startup Deepnote, který vyvíjí pokročilou platformu pro datové analýzy založenou na umělé inteligenci, získal investici ve výši 20 milionů dolarů (přibližně 450 milionů korun). Financování vedl americký venture kapitálový fond Accel s účastí původních investorů Index Ventures a Credo Ventures.

Deepnote založil v roce 2019 Jakub Jurových, absolvent Fakulty informatiky Masarykovy univerzity v Brně. Startup se specializuje na vývoj kolaborativní platformy pro datové vědce, která kombinuje prvky Jupyter Notebooks s pokročilými funkcemi umělé inteligence.

"Tato investice nám umožní rozšířit náš tým a urychlit vývoj nových funkcí, které pomohou datovým týmům pracovat efektivněji," uvedl Jurových. Podle něj plánuje firma v příštích dvou letech zdvojnásobit počet zaměstnanců ze současných 45 na přibližně 90.

Platforma Deepnote si již získala více než 500 000 uživatelů po celém světě, včetně datových týmů ve společnostech jako Spotify, Shopify nebo Harvard University. "Česká republika má skvělé vývojáře a vidíme zde obrovský potenciál zejména v oblasti umělé inteligence," uvedl partner Accel Ventures, který bude nově zasedět v dozorčí radě společnosti.

Deepnote není jediným českým startupem, který v poslední době získal významnou investici. Jen za poslední rok získaly české technologické startupy investice přesahující 2 miliardy korun, což ukazuje na rostoucí zájem zahraničních investorů o český technologický ekosystém.""",
        "title": "Český AI startup Deepnote získal půl miliardy od amerických investorů",
        "summary": "Startup Deepnote, který vyvíjí platformu pro datové analýzy založenou na umělé inteligenci, získal investici 20 milionů dolarů. Financování vedl americký fond Accel. Firma plánuje zdvojnásobit počet zaměstnanců na 90.",
    },
    # 4. Random article about a different topic - Cultural heritage
    {
        "tags": ["kultura", "historie", "UNESCO", "památky", "cestovní ruch"],
        "category": "Cestování",
        "publication_date": datetime(2024, 10, 15, 16, 0),
        "author": "Barbora Tichá",
        "source_site": sources[1]["name"],
        "source_url": f"{sources[1]['domain']}/cestovani/unesco-nove-pamatky-cesko",
        "content": """Barokní hřebčín v Kladrubech nad Labem a hornický region Krušnohoří zaznamenaly v letošní turistické sezóně rekordní návštěvnost. Obě památky, které byly v loňském roce zapsány na Seznam světového dědictví UNESCO, navštívilo dohromady více než 300 000 lidí, což představuje nárůst o 65 % oproti minulému roku.

"Zápis na seznam UNESCO má jednoznačně pozitivní vliv na turistický ruch," uvedla ministryně pro místní rozvoj. "Výrazně se zvýšil zejména počet zahraničních návštěvníků, kteří tvoří asi třetinu všech turistů."

Národní hřebčín v Kladrubech nad Labem, který je domovem nejstaršího původního českého plemene koní - starokladrubského bělouše, prošel v posledních letech rozsáhlou rekonstrukcí. Návštěvníci mohou obdivovat nejen samotné koně, ale také unikátní barokní architekturu a krajinu, která byla komponována specificky pro chov a výcvik ceremoniálních kočárových koní.

Hornický region Krušnohoří zahrnuje pět lokalit na české straně a 17 na německé straně hranic. Dohromady tvoří jedinečný komplex hornických památek, který dokumentuje více než 800 let těžby a zpracování rud. Turisticky nejnavštěvovanější je středověké město Jáchymov, kde byl v 16. století vyražen tolar, který dal jméno americkému dolaru.

"Pro menší obce v příhraničních regionech představuje status UNESCO obrovskou příležitost," uvedl hejtman Karlovarského kraje. "Vidíme nárůst nejen v návštěvnosti, ale i v rozvoji služeb a vytváření nových pracovních míst."

Česká republika má aktuálně na Seznamu světového dědictví UNESCO zapsáno 16 památek, což ji řadí mezi země s nejvyšším počtem památek v přepočtu na rozlohu území.""",
        "title": "Nové české památky UNESCO lákají rekordní počet turistů",
        "summary": "Barokní hřebčín v Kladrubech nad Labem a hornický region Krušnohoří, které byly loni zapsány na Seznam světového dědictví UNESCO, zaznamenaly rekordní návštěvnost. Dohromady je navštívilo více než 300 000 lidí, což představuje nárůst o 65 %.",
    },
]
