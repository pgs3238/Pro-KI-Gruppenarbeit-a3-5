"""
Regelkonfigurationen für regelbasierte automatische Kategorisierung von Transaktionen.

Diese Regeln definieren, welche Keywords und Betragsbereichne zu welchen Kategorien gehören.
Regeln werden nach Priorität sortiert (höhere Werte zuerst).
"""

# Standard-Kategorisierungsregeln
DEFAULT_CATEGORIZATION_RULES = {
    "Gehalt": {
        "keywords": [
            "gehalt",
            "lohn",
            "salary",
            "bonus",
            "provision",
        ],
        "betrag_range": (0, 10000),
        "priority": 10,
    },
    "Miete": {
        "keywords": [
            "miete",
            "wohnung",
            "nebenkosten",
            "warmmiete",
            "kaltmiete",
            "wohnungsmiete",
        ],
        "betrag_range": (-3000, 0),
        "priority": 10,
    },
    "Versicherung": {
        "keywords": [
            "versicherung",
            "krankenkasse",
            "haftpflicht",
            "hausrat",
            "krankenversicherung",
            "kfz-versicherung",
            "lebensversicherung",
        ],
        "betrag_range": (-1000, 0),
        "priority": 9,
    },
    "Lebensmittel": {
        "keywords": [
            "rewe",
            "edeka",
            "aldi",
            "lidl",
            "netto",
            "penny",
            "kaufland",
            "supermarkt",
            "bio",
        ],
        "betrag_range": (-500, 0),
        "priority": 5,
    },
    "Transport": {
        "keywords": [
            "tankstelle",
            "shell",
            "aral",
            "esso",
            "total",
            "db",
            "deutsche bahn",
            "uber",
            "taxi",
            "bus",
            "bahn",
            "ticket",
            "tanken",
        ],
        "betrag_range": (-500, 0),
        "priority": 6,
    },
    "Freizeit": {
        "keywords": [
            "kino",
            "steam",
            "playstation",
            "restaurant",
            "cafe",
            "bar",
            "club",
            "konzert",
            "theater",
            "museum",
            "hobby",
        ],
        "betrag_range": (-300, 0),
        "priority": 3,
    },
    "Strom & Gas": {
        "keywords": [
            "stadtwerke",
            "strom",
            "gas",
            "energie",
            "eon",
            "vattenfall",
            "rwe",
        ],
        "betrag_range": (-300, 0),
        "priority": 8,
    },
    "Internet & Telefon": {
        "keywords": [
            "telekom",
            "vodafone",
            "o2",
            "telefon",
            "handy",
            "internet",
            "mobilfunk",
        ],
        "betrag_range": (-100, 0),
        "priority": 7,
    },
    "Abos & Mitgliedschaften": {
        "keywords": [
            "netflix",
            "spotify",
            "amazon prime",
            "disney+",
            "youtube premium",
            "gym",
            "fitnessstudio",
            "mitgliedschaft",
            "abo",
        ],
        "betrag_range": (-100, 0),
        "priority": 4,
    },
    "Rücklagen": {
        "keywords": [
            "sparplan",
            "rücklage",
            "reserve",
            "notgroschen",
            "sparbuch",
            "tagesgeld",
        ],
        "betrag_range": (-5000, 0),
        "priority": 2,
    },
}
