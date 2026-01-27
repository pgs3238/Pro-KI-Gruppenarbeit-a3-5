# Zentrale Konstanten für die Anwendung

# ==================== FARBEN ====================

# Standard-Farbe für Konten und Kategorien
DEFAULT_COLOR = "#06d6a6"

# Farbpalette für Charts (Sankey, Pie, etc.)
CHART_COLOR_PALETTE = [
    "#3498db",  # Blau
    "#9b59b6",  # Lila
    "#e67e22",  # Orange
    "#1abc9c",  # Türkis
    "#e74c3c",  # Rot
    "#f39c12",  # Gelb-Orange
    "#2ecc71",  # Grün
    "#d35400",  # Dunkel-Orange
    "#8e44ad",  # Dunkel-Lila
    "#16a085",  # Dunkel-Türkis
    "#c0392b",  # Dunkel-Rot
    "#27ae60",  # Dunkel-Grün
    "#2980b9",  # Dunkel-Blau
    "#f1c40f",  # Gelb
    "#e91e63",  # Pink
]

# Spezielle Farben
EXPENSE_COLOR = "#e74c3c"  # Rot für Ausgaben
INCOME_COLOR = "#2ecc71"   # Grün für Einnahmen


# ==================== WÄHRUNGEN ====================

DEFAULT_CURRENCY = "EUR"


# ==================== KATEGORISIERUNG ====================

# Schwellenwert für Auto-Kategorisierung (Anzahl neue Transaktionen)
AUTO_CATEGORIZATION_THRESHOLD = 5

# Mindestanzahl Vorkommen für gelernte Keywords
MIN_KEYWORD_OCCURRENCES = 3
