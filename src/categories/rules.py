"""
Regelkonfigurationen für regelbasierte automatische Kategorisierung von Transaktionen.

Diese Regeln definieren, welche Keywords zu welchen Kategorien gehören.
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
        "priority": 2,
    },
}
