// ============ GLOBALE KONSTANTEN (Frontend) ============

// Deutsche Monatsnamen (vollständig)
const MONTH_NAMES_DE = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
];

// Deutsche Monatsnamen (abgekürzt)
const MONTH_NAMES_DE_SHORT = [
    'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
    'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'
];

// Icon-Mapping für Kategorien
const CATEGORY_ICON_MAP = {
    'Lebensmittel': '🍔',
    'Wohnen': '🏠',
    'Miete': '🏠',
    'Verkehr': '🚗',
    'Transport': '🚗',
    'Unterhaltung': '🎮',
    'Freizeit': '🎮',
    'Gehalt': '💼',
    'Shopping': '🛒',
    'Versicherung': '🛡️',
    'Strom & Gas': '⚡',
    'Internet & Telefon': '📱',
    'Abos & Mitgliedschaften': '📺',
    'Rücklagen': '🏦'
};

// Farben basierend auf Kategorie-Typ
const CATEGORY_COLOR_MAP = {
    'Ausgabe': '#ef4444',
    'Einnahme': '#06d6a6'
};

// Icon-Mapping für Kontotypen
const ACCOUNT_TYPE_ICON_MAP = {
    'girokonto': '🏦',
    'sparkonto': '💰',
    'kreditkarte': '💳',
    'depot': '📈',
    'bargeld': '💵',
    'sonstiges': '🏦'
};

// Standard-Icon falls Typ nicht gefunden
const DEFAULT_ACCOUNT_ICON = '🏦';
