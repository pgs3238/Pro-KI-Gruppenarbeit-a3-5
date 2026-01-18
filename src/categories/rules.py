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
    },
}
