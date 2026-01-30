// ============ GEMEINSAME UTILITY FUNKTIONEN ============

// Zentrale API-Konfiguration (wird von allen JS-Dateien verwendet)
const API_BASE_URL = 'http://localhost:8000/api';

// Zeigt Toast-Benachrichtigung an
function showToast(message, type = 'success', duration = 4000) {
    let container = document.getElementById('toastContainer');
    // Robust: Container bei Bedarf anlegen (z.B. wenn initComponents noch nicht lief)
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
// ============ FORMATIERUNGSFUNKTIONEN ============

// Formatiert Zahl als Währung (EUR)(z.B. "1.234,56 €")
function formatCurrency(amount) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Formatiert IBAN mit Leerzeichen
// @param {string} iban - Die unformatierte IBAN
// @returns {string} Formatierte IBAN
function formatIBAN(iban) {
    if (!iban) return '';
    return iban.match(/.{1,4}/g).join(' ');
}

// Formatiert IBAN-Eingabe (entfernt ungültige Zeichen)(Input-Handler).
// @param {string} iban - Der aktuelle Eingabewert
// @returns {string} Formatierte IBAN für das Input-Feld
function formatIBANInput(iban) {
    const cleaned = iban.replace(/\s/g, '').toUpperCase();
    return cleaned.match(/.{1,4}/g)?.join(' ') || cleaned;
}

// ============ DATUM ============

// Formatiert ein Datum ins deutsche Format.
// @param {Date|string|number} input
// @param {{ pad?: boolean }} options
function formatDateDE(input, options = {}) {
    const { pad = true } = options;
    const d = input instanceof Date ? input : new Date(input);
    if (Number.isNaN(d.getTime())) return '';
    const day = pad ? String(d.getDate()).padStart(2, '0') : String(d.getDate());
    const month = pad ? String(d.getMonth() + 1).padStart(2, '0') : String(d.getMonth() + 1);
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

// ============ SELECT-HELFER ============

// Setzt oder entfernt die 'empty' CSS-Klasse für Select-Elemente.
// Hilft beim Styling von Placeholder-Optionen.
// @param {HTMLSelectElement} select - Das Select-Element
function updateSelectEmptyClass(select) {
    if (!select) return;
    if (select.value === "") {
        select.classList.add('empty');
    } else {
        select.classList.remove('empty');
    }
}

// Aktualisiert Klassen für einzelne Selects
// @param {NodeList|Array} selects - Liste von Select-Elementen
function updateSelectEmptyClasses(selects) {
    if (!selects) return;
    selects.forEach(select => updateSelectEmptyClass(select));
}

// Setzt Klassen für leere Selects (Placeholder-Styling)
// @param {NodeList|Array} selects - Liste von Select-Elementen
function wireSelectEmptyClasses(selects) {
    if (!selects) return;
    selects.forEach(select => {
        updateSelectEmptyClass(select);
        select.addEventListener('change', () => updateSelectEmptyClass(select));
    });
}

// ============ ICONS ============

// Gibt Icon für Kontotyp zurück
// @param {string} typ - Der Kontotyp (Girokonto, Sparkonto, etc.)
// @returns {string} Das Icon als Emoji
function getAccountIcon(typ) {
    const key = (typ || '').toString().toLowerCase();
    return ACCOUNT_TYPE_ICON_MAP[key] || DEFAULT_ACCOUNT_ICON;
}

// ============ API-HELFER ============

// Generische Fetch-Funktion mit Fehlerbehandlung
// @param {string} path - Der API-Pfad (z.B. '/konten')
// @returns {Promise<any>} Die JSON-Antwort
async function apiGetJson(path) {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) {
        throw new Error(`API-Fehler: ${response.status}`);
    }
    return await response.json();
}

// Lädt Konten via API
// @returns {Promise<Array>} Liste der Konten
async function fetchKonten() {
    return await apiGetJson('/konten');
}

// Lädt Kontosaldo via API
// @param {number} kontoId - ID des Kontos
// @returns {Promise<Object>} Saldo-Objekt
async function fetchKontoSaldo(kontoId) {
    return await apiGetJson(`/konten/${kontoId}/saldo`);
}

// Lädt Kategorien via API
// @returns {Promise<Array>} Liste der Kategorien
async function fetchCategories() {
    return await apiGetJson('/categories');
}
