// ============ GEMEINSAME UTILITY FUNKTIONEN ============

// Toast-Benachrichtigungen
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

// ============ MODAL FUNKTIONEN ============

// Generische Modal-Öffnung
function openModal(modalSelector) {
    const modal = document.querySelector(modalSelector);
    if (modal) modal.classList.add('active');
}

// Generische Modal-Schließung
function closeModal(modalSelector, formSelector = null) {
    const modal = document.querySelector(modalSelector);
    if (modal) modal.classList.remove('active');
    
    // Optional: Form zurücksetzen
    if (formSelector) {
        const form = document.querySelector(formSelector);
        if (form) {
            form.reset();
            delete form.dataset.editId;
        }
    }
}