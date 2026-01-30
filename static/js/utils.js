// ============ GEMEINSAME UTILITY FUNKTIONEN ============

// Zentrale API-Konfiguration (wird von allen JS-Dateien verwendet)
const API_BASE_URL = 'http://localhost:8000/api';

// Toast-Benachrichtigungen
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

// Formatiert Beträge als EUR-Währung
function formatCurrency(amount) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Formatiert IBAN mit Leerzeichen
function formatIBAN(iban) {
    if (!iban) return '';
    return iban.match(/.{1,4}/g).join(' ');
}

// Formatiert IBAN-Input während Eingabe
function formatIBANInput(iban) {
    const cleaned = iban.replace(/\s/g, '').toUpperCase();
    return cleaned.match(/.{1,4}/g)?.join(' ') || cleaned;
}

// ============ DATUM ============

/**
 * Formatiert ein Datum ins deutsche Format.
 * @param {Date|string|number} input
 * @param {{ pad?: boolean }} options
 */
function formatDateDE(input, options = {}) {
    const { pad = true } = options;
    const d = input instanceof Date ? input : new Date(input);
    if (Number.isNaN(d.getTime())) return '';
    const day = pad ? String(d.getDate()).padStart(2, '0') : String(d.getDate());
    const month = pad ? String(d.getMonth() + 1).padStart(2, '0') : String(d.getMonth() + 1);
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

// ============ SELECT HELPERS ============

function updateSelectEmptyClass(select) {
    if (!select) return;
    if (select.value === "") {
        select.classList.add('empty');
    } else {
        select.classList.remove('empty');
    }
}

function updateSelectEmptyClasses(selects) {
    if (!selects) return;
    selects.forEach(select => updateSelectEmptyClass(select));
}

function wireSelectEmptyClasses(selects) {
    if (!selects) return;
    selects.forEach(select => {
        updateSelectEmptyClass(select);
        select.addEventListener('change', () => updateSelectEmptyClass(select));
    });
}

// ============ ICONS ============

function getAccountIcon(typ) {
    const key = (typ || '').toString().toLowerCase();
    return ACCOUNT_TYPE_ICON_MAP[key] || DEFAULT_ACCOUNT_ICON;
}

// ============ API HELPERS ============

async function apiGetJson(path) {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) {
        throw new Error(`API-Fehler: ${response.status}`);
    }
    return await response.json();
}

async function fetchKonten() {
    return await apiGetJson('/konten');
}

async function fetchKontoSaldo(kontoId) {
    return await apiGetJson(`/konten/${kontoId}/saldo`);
}

async function fetchCategories() {
    return await apiGetJson('/categories');
}
