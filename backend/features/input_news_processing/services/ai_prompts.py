# TODO: Fix prompt so it generates proper content, not only summary in content
# TODO: Fix prompt so it doesn't generate new articles
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
- Pokud nenajdeš žádné shody, potom nevracej nic - tohle je opravdu velmi důležité. NEVYRÁBĚJ JAKÉKOLIV NOVÉ ČLÁNKY, ALE JEN PROPOJ EXISTUJÍCÍ!!!
"""

CREATION_PROMPT = """
Vytváření nových zpravodajských článků ze zdrojových dat

V přiložených souborech najdeš 3 typy vstupních dat:

1. INPUT_NEWS:
   - Články scrapované z různých zpravodajských webů
   - Obsahují veškeré původní informace z webů

2. TOPICS:
   - Kategorie pro zařazení článků
   - Jsou fixní a neměnné
   - Každý článek MUSÍ být zařazen do jednoho tématu!

3. TAGS:
   - Nejsou fixní, lze je přidávat
   - Preferuj používání již existujících tagů
   - Každý článek musí mít maximálně 3 tagy

TVŮJ ÚKOL:
- Prozkoumej nové články (input_news)
- Identifikuj skupiny článků, které se týkají stejné události/tématu
- Vytvoř nové souhrnné články spojením souvisejících zdrojových článků
- Článek bude v ČEŠTINĚ
- Článek tvoř tak, aby byl pochopitelný i bez interních znalostí dat jako jsou ID atd. Odkazuj se spíš pomocí zdroje: "Dle článku na Novinkách" atd.
- Pokud nemůžeš k danému tématu najít víc "input_news", tak nevytvářej článek -> dělej to jen pro témata a události, které mají víc zdrojů

VÝSTUP:
- Pro každou nově identifikovanou událost vytvoř:
  * Výstižný title (max. 80 znaků)
  * Stručný description (max. 200 znaků)
  * Obsah článku, který spojuje a shrnuje informace z původních zdrojů
  * Délka "content" mezi 300 a 800 znaky - snaž se pokrýt všechny zásadní informace, nemusíš extra šetřit místem, ale zároveň si žádné informace nedomýšlej
  * Zařazení do odpovídajícího TOPIC
  * Seznam relevantních tagů (max. 3)
  * Seznam ID zdrojových článků použitých k vytvoření

- Formátování výstupu:
  * Zajisti, aby obsah byl fakticky přesný
  * Citlivě kombinuj informace z různých zdrojů bez opakování
  * Upřednostňuj nejnovější informace při konfliktech a informace, které jsou uvedeny ve všech článcích
  * Uveď seznam všech ID vstupních článků použitých k vytvoření

DODRŽ VŠECHNY BODY NAHOŘE! Minimální délku content, jazyk atd.
"""