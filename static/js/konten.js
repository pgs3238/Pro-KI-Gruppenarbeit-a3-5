// ============ BEISPIELDATEN ============
const accountsData = [
    {
        id: 1,
        name: 'Hauptkonto',
        typ: 'girokonto',
        bank: 'Sparkasse',
        iban: 'DE89370400440532013000',
        saldo: 2450.67,
        waehrung: 'EUR',
        farbe: '#06d6a6'
    },
    {
        id: 2,
        name: 'Sparkonto',
        typ: 'sparkonto',
        bank: 'Deutsche Bank',
        iban: 'DE75512108001245126199',
        saldo: 15000.00,
        waehrung: 'EUR',
        farbe: '#3b82f6'
    },
    {
        id: 3,
        name: 'Kreditkarte',
        typ: 'kreditkarte',
        bank: 'Visa',
        iban: 'DE44500105175407324931',
        saldo: -342.50,
        waehrung: 'EUR',
        farbe: '#8b5cf6'
    },
    {
        id: 4,
        name: 'Depot',
        typ: 'depot',
        bank: 'Trade Republic',
        iban: null,
        saldo: 8750.25,
        waehrung: 'EUR',
        farbe: '#f59e0b'
    },
    {
        id: 5,
        name: 'Bargeld',
        typ: 'bargeld',
        bank: null,
        iban: null,
        saldo: 250.00,
        waehrung: 'EUR',
        farbe: '#ef4444'
    }
];

// Konten Icons basierend auf Typ
const accountIcons = {
    'girokonto': '💳',
    'sparkonto': '💰',
    'kreditkarte': '💸',
    'depot': '📈',
    'bargeld': '💵',
    'sonstiges': '🏦'
};

// Konten laden und anzeigen
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
function formatCurrency(amount) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

function formatIBAN(iban) {
    if (!iban) return '';
    return iban.match(/.{1,4}/g).join(' ');
}

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
    document.querySelector('input[name="saldo"]').value = account.saldo;
    document.querySelector('select[name="waehrung"]').value = account.waehrung;
    document.querySelector(`input[name="farbe"][value="${account.farbe}"]`).checked = true;

    document.querySelector('.modal-title').textContent = 'Konto bearbeiten';
    document.getElementById('accountForm').dataset.editId = id;

    openAccountModal();
}

// Konto löschen
function deleteAccount(id) {
    if (confirm('Möchten Sie dieses Konto wirklich löschen?')) {
        const index = accountsData.findIndex(a => a.id === id);
        if (index !== -1) {
            accountsData.splice(index, 1);
            loadAccounts();
            showToast('Konto erfolgreich gelöscht!', 'success');
        }
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
        const account = accountsData.find(a => a.id === parseInt(editId));
        if (account) {
            Object.assign(account, accountData);
            showToast('Konto erfolgreich aktualisiert!', 'success');
        }
    } else {
        const newId = Math.max(...accountsData.map(a => a.id), 0) + 1;
        accountsData.push({
            id: newId,
            ...accountData
        });
        showToast('Konto erfolgreich hinzugefügt!', 'success');
    }

    loadAccounts();
    closeAccountModal();
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

function formatIBANInput(iban) {
    const cleaned = iban.replace(/\s/g, '').toUpperCase();
    return cleaned.match(/.{1,4}/g)?.join(' ') || cleaned;
}

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
loadAccounts();

// ============ TOAST NOTIFICATIONS ============

function showToast(message, type = 'success', duration = 10000) {
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
