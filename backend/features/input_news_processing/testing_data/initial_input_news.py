from datetime import datetime

from features.input_news_processing.domain.schemas import InputNews
from features.input_news_processing.testing_data.common_testing_data import sources

INITIAL_INPUT_ARTICLES = [
    # Group 1: Three articles about the same event - Significant flooding in Moravia
    {
        "tags": ["povodně", "Morava", "počasí", "krizová situace"],
        "category": "Domácí",
        "publication_date": datetime(2024, 10, 5, 8, 30),
        "author": "Jan Novák",
        "source_site": sources[0]["name"],
        "source_url": f"{sources[0]['domain']}/zpravy/domaci/povoden-morava-evakuace",
        "content": """Jižní Morava čelí největším povodním za posledních deset let. Po několikadenních vytrvalých deštích se řeky Morava a Dyje vylily z břehů a zaplavily několik obcí. Hasiči evakuovali přes 200 lidí.

Meteorologové varují, že situace se může ještě zhoršit, protože na horním toku řeky Moravy stále prší. Hejtman Jihomoravského kraje vyhlásil stav nebezpečí pro celý region.

"Situace je vážná, ale pod kontrolou. Všechny složky integrovaného záchranného systému jsou v pohotovosti," uvedl hejtman. Podle něj budou škody jít do stovek milionů korun.

V některých oblastech spadlo za posledních 48 hodin až 150 mm srážek, což je více než měsíční úhrn v tomto období. Předpověď počasí na další dny není příznivá a očekává se další déšť.""",
        "title": "Jižní Moravu zasáhly ničivé povodně, evakuováno 200 lidí",
        "summary": "Silné deště způsobily na jižní Moravě rozsáhlé povodně. Řeky Morava a Dyje se vylily z břehů a zaplavily několik obcí. Evakuováno bylo více než 200 obyvatel.",
    },
    {
        "tags": ["záplavy", "Jihomoravský kraj", "evakuace", "počasí", "hasiči"],
        "category": "Zprávy z regionů",
        "publication_date": datetime(2024, 10, 5, 9, 45),
        "author": "Petra Svobodová",
        "source_site": sources[1]["name"],
        "source_url": f"{sources[1]['domain']}/clanek/povoden-jizni-morava-zachranne-prace",
        "content": """Několik obcí na jižní Moravě se potýká s následky povodní. Nejvíce postižené jsou obce Lanžhot, Břeclav a Hodonín. Hladina řeky Moravy na některých místech dosáhla třetího stupně povodňové aktivity.

Hasiči během noci evakuovali přes 200 obyvatel z ohrožených oblastí. Na některých místech museli použít i vrtulníky, protože silnice byly neprůjezdné. Evakuovaní lidé našli dočasné útočiště v tělocvičnách místních škol.

"Museli jsme opustit dům během noci. Stihli jsme vzít jen nejdůležitější věci a dokumenty," řekla paní Nováková z Lanžhota. "Nevíme, co s naším domem bude, je to hrozné."

Podle meteorologů v následujících 24 hodinách může spadnout dalších 30 až 50 mm srážek. Premiér oznámil, že navštíví postižené oblasti zítra dopoledne.""",
        "title": "Dramatické záplavy na jihu Moravy, hasiči evakuovali stovky lidí",
        "summary": "Silné deště způsobily kritickou situaci na jižní Moravě. Nejvíce zasaženy jsou obce Lanžhot, Břeclav a Hodonín. Hasiči evakuovali více než 200 obyvatel z ohrožených oblastí.",
    },
    {
        "tags": ["povodeň", "Morava", "škody", "pomoc", "krizový štáb"],
        "category": "Zpravodajství",
        "publication_date": datetime(2024, 10, 5, 12, 15),
        "author": "Martin Procházka",
        "source_site": sources[2]["name"],
        "source_url": f"{sources[2]['domain']}/zpravy/povoden-morava-skody-pomoc",
        "content": """Povodně na jižní Moravě způsobily škody už za několik set milionů korun. První odhady hovoří o 300 milionech, ale konečná částka bude zřejmě vyšší. Nejvíce poškozená je infrastruktura - zatopené silnice, stržené mosty a poškozené železniční tratě.

Ministerstvo financí uvolnilo 50 milionů korun na okamžitou pomoc postiženým obcím. Armáda vyslala 150 vojáků s těžkou technikou, aby pomohli s odklízením následků a stavbou protipovodňových hrází.

Meteorologové upozorňují, že v příštích dnech hrozí další srážky. "Půda je již nasycená vodou, takže i menší srážky mohou způsobit další problémy," uvedl meteorolog Český hydrometeorologický ústav.

Voda zatopila také čistírnu odpadních vod v Břeclavi, což může způsobit další komplikace včetně znečištění. Hygienici varují před používáním vody ze zatopených studní.

Dobrovolníci z celé republiky se hlásí k pomoci. Humanitární organizace vyhlásily sbírky na pomoc postiženým.""",
        "title": "Povodně na Moravě: Škody jdou do stovek milionů, armáda nasadila vojáky",
        "summary": "Povodně na jižní Moravě způsobily škody za stovky milionů korun. Ministerstvo financí uvolnilo 50 milionů na okamžitou pomoc. Na místě pomáhá 150 vojáků s těžkou technikou.",
    },
    # Group 2: Two articles about the same event - New electric car factory
    {
        "tags": ["ekonomika", "průmysl", "automobilový průmysl", "investice"],
        "category": "Ekonomika",
        "publication_date": datetime(2024, 10, 6, 10, 0),
        "author": "Karel Veselý",
        "source_site": sources[0]["name"],
        "source_url": f"{sources[0]['domain']}/ekonomika/tovarna-elektromobily-investice",
        "content": """Jihokorejský výrobce automobilů Hyundai oznámil plány na výstavbu nové továrny na elektromobily v České republice. Investice v hodnotě přibližně 20 miliard korun by měla vytvořit až 2500 nových pracovních míst.

Továrna má být postavena v průmyslové zóně u Ostravy a výroba by měla být zahájena v roce 2026. Jedná se o jednu z největších zahraničních investic v Česku za poslední dekádu.

"Tato investice potvrzuje, že Česká republika je atraktivní destinací pro výrobu automobilů budoucnosti," uvedl ministr průmyslu a obchodu. Podle něj bude mít investice značný multiplikační efekt a podpoří i další firmy v regionu.

Hyundai plánuje v nové továrně vyrábět dva modely elektromobilů určené pro evropský trh. Společnost očekává, že roční produkce dosáhne až 300 000 vozů.""",
        "title": "Hyundai postaví v Česku novou továrnu na elektromobily za 20 miliard",
        "summary": "Jihokorejská automobilka Hyundai oznámila investici 20 miliard korun do nové továrny na elektromobily v průmyslové zóně u Ostravy. Vzniknout by mělo 2500 pracovních míst.",
    },
    {
        "tags": [
            "Hyundai",
            "elektromobily",
            "Ostrava",
            "pracovní místa",
            "zelená ekonomika",
        ],
        "category": "Byznys",
        "publication_date": datetime(2024, 10, 6, 11, 30),
        "author": "Lucie Novotná",
        "source_site": sources[2]["name"],
        "source_url": f"{sources[2]['domain']}/byznys/hyundai-investice-elektromobily-ostrava",
        "content": """Jihokorejská automobilka Hyundai oficiálně potvrdila, že v České republice postaví novou továrnu zaměřenou výhradně na výrobu elektrických vozidel. Investice přesáhne 20 miliard korun a vznikne v průmyslové zóně nedaleko Ostravy.

Podle generálního ředitele Hyundai Motor Czech bude nový závod využívat nejmodernější technologie a automatizaci. "Naším cílem je vytvořit nejefektivnější továrnu na výrobu elektromobilů v Evropě," uvedl.

Stavba továrny by měla začít příští rok a první automobily by měly sjíždět z výrobních linek v roce 2026. Kromě 2500 přímých pracovních míst odhadují ekonomové, že investice nepřímo vytvoří dalších 5000 pracovních míst u dodavatelů.

Moravskoslezský kraj vítá tuto investici jako významný impuls pro region, který se dlouhodobě potýká s transformací od těžkého průmyslu k modernějším odvětvím. "Je to potvrzení, že náš region má budoucnost v high-tech průmyslu," uvedl hejtman kraje.

Automobilka už v České republice provozuje závod v Nošovicích, kde vyrábí modely i30, Tucson a Kona. Nová továrna však bude zaměřena výhradně na elektromobily a bude fungovat nezávisle na stávající výrobě.""",
        "title": "Hyundai investuje 20 miliard do výroby elektromobilů v Ostravě",
        "summary": "Automobilka Hyundai postaví v průmyslové zóně u Ostravy novou továrnu na výrobu elektromobilů. Investice přesáhne 20 miliard korun a vytvoří 2500 přímých pracovních míst.",
    },
    # Group 3: Two articles about the same event - Cultural festival
    {
        "tags": ["kultura", "festival", "Praha", "umění", "mezinárodní"],
        "category": "Kultura",
        "publication_date": datetime(2024, 10, 7, 15, 0),
        "author": "Eva Dvořáková",
        "source_site": sources[1]["name"],
        "source_url": f"{sources[1]['domain']}/kultura/festival-signal-praha-svetelne-instalace",
        "content": """Dnes večer začíná v Praze jedenáctý ročník festivalu Signal, který na čtyři dny promění hlavní město v galerii světelného umění pod širým nebem. Návštěvníci se mohou těšit na dvacet instalací od umělců z celého světa.

"Letošní téma festivalu je 'Proměny města', což reflektuje, jak se urban prostor mění v čase a jak na něj reagují umělci," uvedla ředitelka festivalu Marie Víchová.

Novinkou letošního ročníku je rozšíření festivalu mimo centrum Prahy. Některé instalace budou k vidění i v Holešovicích a Karlíně. Největší zájem je tradičně o videomapping na fasádě Rudolfina, který letos připravil japonský umělecký kolektiv TeamLab.

Festival potrvá do neděle a podle organizátorů by mohl přilákat až 500 tisíc návštěvníků. Vstup na většinu instalací je zdarma, pouze na některé speciální projekce je potřeba zakoupit vstupenku.""",
        "title": "Festival Signal rozsvítí Prahu, nabídne dvacet světelných instalací",
        "summary": "V Praze začíná jedenáctý ročník festivalu Signal. Na čtyři dny promění hlavní město v galerii světelného umění pod širým nebem. Návštěvníci uvidí dvacet instalací od umělců z celého světa.",
    },
    {
        "tags": [
            "Signal festival",
            "světelné umění",
            "Praha",
            "videomapping",
            "kultura",
        ],
        "category": "Události",
        "publication_date": datetime(2024, 10, 7, 17, 45),
        "author": "Tomáš Černý",
        "source_site": sources[0]["name"],
        "source_url": f"{sources[0]['domain']}/kultura/festival-signal-zahajeni-praha",
        "content": """Jedenáctý ročník festivalu Signal byl dnes večer slavnostně zahájen v centru Prahy. Úvodní ceremoniál se konal na Staroměstském náměstí, kde byla představena hlavní instalace letošního ročníku - interaktivní světelná skulptura "Metamorfóza" od britského umělce Patricka Johnsona.

"Tato instalace reaguje na pohyb lidí kolem ní a mění se podle jejich aktivity. Je to metafora toho, jak město žije a dýchá díky svým obyvatelům," vysvětlil Johnson.

Festival nabízí celkem dvacet různých instalací rozmístěných po celé Praze, včetně videomappingu na fasádě Rudolfina, světelné show na Vltavě a různých interaktivních expozic v ulicích města.

Podle odhadů organizátorů navštívilo zahajovací večer asi 50 tisíc lidí. "Jsme překvapeni tak velkým zájmem už první den. Vypadá to, že letošní ročník bude rekordní," uvedla ředitelka festivalu.

Kvůli velkému zájmu byly posíleny linky MHD a centrum města je dočasně uzavřeno pro automobilovou dopravu. Festival potrvá do neděle a vstup na většinu instalací je zdarma.""",
        "title": "Signal festival zahájen, první večer přilákal 50 tisíc lidí",
        "summary": "V Praze byl zahájen jedenáctý ročník festivalu Signal. První večer navštívilo přibližně 50 tisíc lidí. Hlavní instalací je interaktivní světelná skulptura 'Metamorfóza' na Staroměstském náměstí.",
    },
    # Three individual articles about different events
    {
        "tags": ["sport", "fotbal", "reprezentace", "kvalifikace", "EURO"],
        "category": "Sport",
        "publication_date": datetime(2024, 10, 8, 22, 30),
        "author": "Jakub Horák",
        "source_site": sources[1]["name"],
        "source_url": f"{sources[1]['domain']}/sport/fotbal-cesko-polsko-kvalifikace",
        "content": """Česká fotbalová reprezentace zvítězila v klíčovém zápase kvalifikace na EURO 2024 nad Polskem 2:1. Góly vstřelili Patrik Schick a Tomáš Souček, za hosty snižoval v závěru Robert Lewandowski.

Zápas se hrál před vyprodanou Eden Arénou v Praze a čeští fotbalisté předvedli jeden z nejlepších výkonů pod vedením trenéra Ivana Haška. Díky tomuto vítězství se národní tým posunul na druhé místo kvalifikační skupiny a výrazně si vylepšil pozici v boji o postup na evropský šampionát.

"Byl to těžký zápas, ale zvládli jsme to jako tým. Každý nechal na hřišti maximum a to rozhodlo," řekl po zápase kapitán Tomáš Souček.

Čeští fotbalisté mají před sebou ještě dva zápasy - v listopadu se utkají venku s Moldavskem a doma s Albánií. K přímému postupu na EURO potřebují získat alespoň čtyři body.""",
        "title": "Čeští fotbalisté porazili Polsko 2:1 a přiblížili se postupu na EURO",
        "summary": "Česká fotbalová reprezentace zvítězila v kvalifikačním zápase na EURO 2024 nad Polskem 2:1. Góly vstřelili Schick a Souček. Češi se posunuli na druhé místo kvalifikační skupiny.",
    },
    {
        "tags": ["zdraví", "medicína", "výzkum", "Parkinsonova choroba", "neurologie"],
        "category": "Věda a zdraví",
        "publication_date": datetime(2024, 10, 9, 14, 15),
        "author": "MUDr. Jana Králová",
        "source_site": sources[2]["name"],
        "source_url": f"{sources[2]['domain']}/veda-a-zdravi/parkinsonova-choroba-novy-lek-vyzkum",
        "content": """Tým českých vědců z Neurologického ústavu v Praze ve spolupráci s kolegy z Německa a USA dosáhl významného pokroku při vývoji nového léku na Parkinsonovu chorobu. Experimentální preparát v předklinických testech prokázal schopnost zpomalit odumírání neuronů produkujících dopamin, což je klíčový proces při rozvoji této nemoci.

"Naše látka působí na zcela jiném principu než dosavadní léky. Nezaměřuje se pouze na symptomy, ale přímo na příčinu nemoci, tedy na odumírání neuronů," vysvětluje prof. Jiří Novák, vedoucí výzkumného týmu.

Podle předběžných výsledků by nový lék mohl nejen zmírnit příznaky Parkinsonovy choroby, ale také zpomalit její průběh, což by byl zásadní průlom v léčbě tohoto onemocnění. V současnosti dostupné léky totiž pouze potlačují příznaky, ale nedokážou zastavit progresi nemoci.

Klinické testy na lidských pacientech by měly začít příští rok. "Pokud všechno půjde podle plánu, nový lék by mohl být dostupný pro pacienty do pěti let," dodává prof. Novák.""",
        "title": "Čeští vědci dosáhli průlomu ve vývoji léku na Parkinsonovu chorobu",
        "summary": "Tým vědců z Neurologického ústavu v Praze vyvinul experimentální lék, který v předklinických testech dokázal zpomalit odumírání neuronů u Parkinsonovy choroby. Klinické testy začnou příští rok.",
    },
    {
        "tags": ["počasí", "klimatická změna", "meteorologie", "rekordy", "sucho"],
        "category": "Domácí zprávy",
        "publication_date": datetime(2024, 10, 10, 9, 0),
        "author": "Michal Žák",
        "source_site": sources[0]["name"],
        "source_url": f"{sources[0]['domain']}/zpravy/domaci/leto-2023-nejteplejsi-sucho",
        "content": """Léto 2023 bylo podle údajů Českého hydrometeorologického ústavu nejteplejším létem od začátku měření v roce 1775. Průměrná teplota byla o 2,8 stupně Celsia vyšší než dlouhodobý normál.

"Takový odchylka od normálu je opravdu mimořádná a potvrzuje trend oteplování klimatu," uvedl klimatolog Pavel Zahradníček. "Zejména měsíc červenec byl extrémní, kdy průměrná teplota přesáhla 22 stupňů Celsia."

Vysoké teploty byly doprovázeny také výrazným suchem. V některých regionech, zejména na jižní Moravě a ve středních Čechách, spadlo za celé léto méně než 50 % obvyklých srážek. To způsobilo problémy zemědělcům a vedlo k rekordně nízkým stavům řek.

Meteorologové varují, že podobné extrémy budou s postupující klimatickou změnou stále častější. "To, co bylo dříve považováno za výjimečný rok, se stává novým normálem," dodal Zahradníček.

Ministerstvo zemědělství již oznámilo, že připravuje kompenzace pro zemědělce postižené suchem. Předběžné odhady škod na úrodě hovoří o několika miliardách korun.""",
        "title": "Léto 2023 bylo nejteplejší v historii měření, provázelo ho extrémní sucho",
        "summary": "Podle ČHMÚ bylo léto 2023 nejteplejším létem od začátku měření v roce 1775. Průměrná teplota byla o 2,8 stupně Celsia vyšší než dlouhodobý normál. Výrazné sucho způsobilo škody v zemědělství.",
    },
]


def load_initial_input_news_data() -> list[InputNews]:
    # Convert the data back to Pydantic models
    articles = []
    for article_dict in INITIAL_INPUT_ARTICLES:
        # Convert string back to datetime
        article_dict["publication_date"] = datetime.fromisoformat(
            article_dict["publication_date"]
        )

        # Create Pydantic model
        article = InputNews(**article_dict)
        articles.append(article)

    return articles
