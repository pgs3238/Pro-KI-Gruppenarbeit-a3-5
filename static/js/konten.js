// ============ KONTEN JAVASCRIPT ============
// Nutzt API_BASE_URL aus utils.js

// ============ BEISPIELDATEN (FALLBACK) ============
let accountsData = [];

// Account Icons basierend auf Typ
const accountIcons = {
    'girokonto': '💳',
    'sparkonto': '💰',
    'kreditkarte': '💸',
    'depot': '📈',
    'bargeld': '💵',
    'sonstiges': '🏦'
};

// ============ API FUNKTIONEN ============

async function loadAccountsFromAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/konten`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        
        const konten = await response.json();
        
        // Konvertiere API-Daten ins Frontend-Format
        accountsData = konten.map(konto => ({
            id: konto.id,
            name: konto.kontoname,
            typ: konto.kontotyp.toLowerCase().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue'),
            bank: konto.bankname || null,
            iban: konto.kontonummer || null,
            initialstand: konto.kontostand,  // Speichere Initialstand
            saldo: konto.kontostand,  // Wird gleich mit aktuellen Saldo überschrieben
            waehrung: konto.waehrung,
            farbe: konto.farbe || '#06d6a6'
        }));
        
        // Lade den aktuellen Saldo (initialstand + transaktionen) für jedes Konto
        for (let account of accountsData) {
            try {
                const saldoResponse = await fetch(`${API_BASE_URL}/konten/${account.id}/saldo`);
                if (saldoResponse.ok) {
                    const saldoData = await saldoResponse.json();
                    account.saldo = saldoData.aktueller_saldo;  // Überschreibe mit aktuellem Wert
                }
            } catch (error) {
                console.warn(`Fehler beim Laden des Saldos für Konto ${account.id}:`, error);
            }
        }
        
        loadAccounts();
    } catch (error) {
        console.error('Fehler beim Laden der Konten:', error);
        // Fallback zu leeren Daten
        accountsData = [];
        loadAccounts();
    }
}

async function createAccountAPI(accountData) {
    try {
        // Konvertiere Frontend-Daten ins API-Format
        const apiData = {
            kontoname: accountData.name,
            kontotyp: accountData.typ.charAt(0).toUpperCase() + accountData.typ.slice(1),
            bankname: accountData.bank || null,
            kontonummer: (accountData.iban || '').replace(/\s/g, ''),  // Entferne Leerzeichen
            kontostand: accountData.saldo,
            waehrung: accountData.waehrung,
            bic: null,
            farbe: accountData.farbe
        };
        
        const response = await fetch(`${API_BASE_URL}/konten`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Erstellen des Kontos');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fehler beim Erstellen des Kontos:', error);
        throw error;
    }
}

async function updateAccountAPI(konto_id, accountData) {
    try {
        const apiData = {
            kontoname: accountData.name,
            kontotyp: accountData.typ.charAt(0).toUpperCase() + accountData.typ.slice(1),
            bankname: accountData.bank || null,
            kontonummer: (accountData.iban || '').replace(/\s/g, ''),  // Entferne Leerzeichen
            kontostand: accountData.saldo,
            waehrung: accountData.waehrung,
            farbe: accountData.farbe
        };
        
        const response = await fetch(`${API_BASE_URL}/konten/${konto_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Aktualisieren des Kontos');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fehler beim Aktualisieren des Kontos:', error);
        throw error;
    }
}

async function deleteAccountAPI(konto_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/konten/${konto_id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Löschen des Kontos');
        }
    } catch (error) {
        console.error('Fehler beim Löschen des Kontos:', error);
        throw error;
    }
}

// ============ KONTEN LADEN UND ANZEIGEN ============
function loadAccounts() {
    const grid = document.getElementById('accountsGrid');
    grid.innerHTML = '';

    // Gesamtsaldo berechnen
    const totalSaldo = accountsData.reduce((sum, acc) => sum + acc.saldo, 0);

    // Übersichtskarte
    const summaryCard = document.createElement('div');
    summaryCard.className = 'account-card summary-card';
    summaryCard.innerHTML = `
        <div class="account-card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <span class="account-icon">💼</span>
            <div class="account-actions">
                <span class="account-badge">${accountsData.length} Konten</span>
            </div>
        </div>
        <div class="account-card-body">
            <h3 class="account-name">Gesamtbetrag</h3>
            <div class="account-balance-large">${formatCurrency(totalSaldo)}</div>
        </div>
    `;
    grid.appendChild(summaryCard);

    // Konten-Karten
    accountsData.forEach(account => {
        const card = document.createElement('div');
        card.className = 'account-card';
        card.innerHTML = `
            <div class="account-card-header" style="background: ${account.farbe};">
                <span class="account-icon">${accountIcons[account.typ] || '🏦'}</span>
                <div class="account-actions">
                    <button class="account-action-btn" onclick="editAccount(${account.id})" title="Bearbeiten">✏️</button>
                    <button class="account-action-btn" onclick="deleteAccount(${account.id})" title="Löschen">🗑️</button>
                </div>
            </div>
            <div class="account-card-body">
                <h3 class="account-name">${account.name}</h3>
                <div class="account-balance ${account.saldo >= 0 ? 'positive' : 'negative'}">${formatCurrency(account.saldo)}</div>
                <div class="account-details">
                    ${account.bank ? `<div class="detail-item"><span class="detail-label">🏦</span><span>${account.bank}</span></div>` : ''}
                    ${account.iban ? `<div class="detail-item"><span class="detail-label">💳</span><span>${formatIBAN(account.iban)}</span></div>` : ''}
                    <div class="detail-item">
                        <span class="detail-label">Typ:</span>
                        <span class="account-badge">${formatAccountType(account.typ)}</span>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Hilfsfunktionen
function formatAccountType(typ) {
    const types = {
        'girokonto': 'Girokonto',
        'sparkonto': 'Sparkonto',
        'kreditkarte': 'Kreditkarte',
        'depot': 'Depot',
        'bargeld': 'Bargeld',
        'sonstiges': 'Sonstiges'
    };
    return types[typ] || typ;
}

// Konto bearbeiten
function editAccount(id) {
    const account = accountsData.find(a => a.id === id);
    if (!account) return;

    document.querySelector('input[name="name"]').value = account.name;
    document.querySelector('select[name="typ"]').value = account.typ;
    document.querySelector('input[name="iban"]').value = account.iban || '';
    document.querySelector('input[name="bank"]').value = account.bank || '';
    document.querySelector('input[name="saldo"]').value = account.initialstand;  // Nutze initialstand statt saldo
    document.querySelector('select[name="waehrung"]').value = account.waehrung;
    document.querySelector(`input[name="farbe"][value="${account.farbe}"]`).checked = true;

    document.querySelector('.modal-title').textContent = 'Konto bearbeiten';
    document.getElementById('accountForm').dataset.editId = id;

    openAccountModal();
}

// Konto löschen
function deleteAccount(id) {
    if (confirm('Möchten Sie dieses Konto wirklich löschen?')) {
        deleteAccountAPI(id)
            .then(() => {
                showToast('Konto erfolgreich gelöscht!', 'success');
                loadAccountsFromAPI();
            })
            .catch(error => {
                showToast(`Fehler beim Löschen: ${error.message}`, 'error');
            });
    }
}

// Modal Funktionen
const modal = document.getElementById('accountModal');
const selects = document.querySelectorAll('select.form-control');

function openAccountModal() {
    modal.classList.add('active');
}

function closeAccountModal() {
    modal.classList.remove('active');
    document.getElementById('accountForm').reset();
    document.querySelector('.modal-title').textContent = 'Konto hinzufügen';
    delete document.getElementById('accountForm').dataset.editId;
    updateSelectColors();
}

modal.addEventListener('click', (e) => {
    if (e.target === modal) closeAccountModal();
});

// Form Submit
document.getElementById('accountForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const form = e.target;
    const editId = form.dataset.editId;

    const accountData = {
        name: document.querySelector('input[name="name"]').value,
        typ: document.querySelector('select[name="typ"]').value,
        iban: document.querySelector('input[name="iban"]').value || null,
        bank: document.querySelector('input[name="bank"]').value || null,
        saldo: parseFloat(document.querySelector('input[name="saldo"]').value),
        waehrung: document.querySelector('select[name="waehrung"]').value,
        farbe: document.querySelector('input[name="farbe"]:checked').value
    };

    if (editId) {
        // Aktualisierung
        updateAccountAPI(parseInt(editId), accountData)
            .then(() => {
                showToast('Konto erfolgreich aktualisiert!', 'success');
                loadAccountsFromAPI();
                closeAccountModal();
            })
            .catch(error => {
                showToast(`Fehler beim Aktualisieren: ${error.message}`, 'error');
            });
    } else {
        // Neue Konten erstellen
        createAccountAPI(accountData)
            .then(() => {
                showToast('Konto erfolgreich hinzugefügt!', 'success');
                loadAccountsFromAPI();
                closeAccountModal();
            })
            .catch(error => {
                showToast(`Fehler beim Erstellen: ${error.message}`, 'error');
            });
    }
});

// Select Placeholder Styling
function updateSelectColor(select) {
    if (select.value === "") {
        select.classList.add('empty');
    } else {
        select.classList.remove('empty');
    }
}

function updateSelectColors() {
    selects.forEach(select => updateSelectColor(select));
}

selects.forEach(select => {
    updateSelectColor(select);
    select.addEventListener('change', () => updateSelectColor(select));
});

document.getElementById('accountForm').addEventListener('reset', () => {
    setTimeout(() => updateSelectColors(), 0);
});

// IBAN Formatierung
const ibanInput = document.querySelector('input[name="iban"]');

ibanInput.addEventListener('input', (e) => {
    const cursorPos = e.target.selectionStart;
    const oldValue = e.target.value;
    const oldLength = oldValue.length;
    
    e.target.value = formatIBANInput(e.target.value);
    
    const newLength = e.target.value.length;
    const newCursorPos = cursorPos + (newLength - oldLength);
    e.target.setSelectionRange(newCursorPos, newCursorPos);
});

// Suchfunktion
const searchBox = document.getElementById('searchBox');
const searchIcon = document.querySelector('.search-icon');

if (searchBox && searchIcon) {
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        searchIcon.style.display = searchTerm ? 'none' : 'block';
        
        const cards = document.querySelectorAll('.account-card:not(.summary-card)');
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Initial laden
loadAccountsFromAPI();

// ============ TOAST NOTIFICATIONS ============

function showToast(message, type = 'success', duration = 4000) {
    const container = document.getElementById('toastContainer');
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
// Initial laden
loadAccountsFromAPI();