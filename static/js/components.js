// ============ SHARED COMPONENTS ============
// Zentrale Komponenten die auf allen Seiten verwendet werden

/**
 * Erstellt die Sidebar-Navigation
 * @param {string} activePage - ID der aktiven Seite (overview, transactions, categories, accounts, forecast, chatbot)
 */
function renderSidebar(activePage) {
    const navItems = [
        { id: 'overview', icon: '📈', label: 'Übersicht', href: 'index.html' },
        { id: 'transactions', icon: '💳', label: 'Transaktionen', href: 'transactions.html' },
        { id: 'categories', icon: '🏷️', label: 'Kategorien', href: 'kategorien.html' },
        { id: 'accounts', icon: '🏦', label: 'Konten', href: 'konten.html' },
        { id: 'forecast', icon: '📉', label: 'Zinsprognose', href: 'zinsrechner.html' },
        { id: 'chatbot', icon: '💬', label: 'Finanz-Buddy', href: 'finanz-buddy.html' }
    ];

    const navItemsHtml = navItems.map(item => `
        <li class="nav-item">
            <button class="nav-link${item.id === activePage ? ' active' : ''}" 
                    id="nav-${item.id}"
                    ${item.id !== activePage ? `onclick="window.location.href='${item.href}'"` : ''}>
                <span class="nav-icon">${item.icon}</span>
                <span>${item.label}</span>
            </button>
        </li>
    `).join('');

    return `
        <aside class="sidebar">
            <div class="logo">
                <span>📊</span>
                <span>FINLY</span>
            </div>
            <ul class="nav-items">
                ${navItemsHtml}
            </ul>
        </aside>
    `;
}

/**
 * Erstellt den Header mit Settings-Button
 */
function renderHeader() {
    return `
        <header class="header">
            <div class="header-right">
                <button class="icon-btn" onclick="document.getElementById('apiKeyModal').style.display='flex'">⚙️</button>
            </div>
        </header>
    `;
}

/**
 * Erstellt das API-Key Modal
 */
function renderApiKeyModal() {
    return `
        <div id="apiKeyModal" class="api-key-modal">
            <div class="api-modal-content">
                <div class="api-modal-header">
                    <h2>API-Einstellungen</h2>
                    <button class="api-modal-close" onclick="document.getElementById('apiKeyModal').style.display='none'">&times;</button>
                </div>
                <div class="api-modal-body">
                    <label class="api-label">Gemini API Key für Finanz-Buddy</label>
                    <input type="password" id="apiKeyInput" class="api-input" placeholder="AIza..." />
                    <small class="api-hint">Ihr API-Key wird in der .env-Datei auf dem Server gespeichert.</small>
                </div>
                <div class="api-modal-footer">
                    <button class="api-btn api-btn-cancel" onclick="document.getElementById('apiKeyModal').style.display='none'">Abbrechen</button>
                    <button class="api-btn api-btn-save">Speichern</button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Erstellt den Toast Container
 */
function renderToastContainer() {
    return `<div id="toastContainer" class="toast-container"></div>`;
}

/**
 * Initialisiert alle gemeinsamen Komponenten auf der Seite
 * @param {string} activePage - ID der aktiven Seite
 */
function initComponents(activePage) {
    // Sidebar einfügen
    const sidebarPlaceholder = document.getElementById('sidebar-placeholder');
    if (sidebarPlaceholder) {
        sidebarPlaceholder.outerHTML = renderSidebar(activePage);
    }

    // Header einfügen
    const headerPlaceholder = document.getElementById('header-placeholder');
    if (headerPlaceholder) {
        headerPlaceholder.outerHTML = renderHeader();
    }

    // API Modal einfügen (vor </body>)
    if (!document.getElementById('apiKeyModal')) {
        document.body.insertAdjacentHTML('beforeend', renderApiKeyModal());
    }

    // Toast Container einfügen (vor </body>)
    if (!document.getElementById('toastContainer')) {
        document.body.insertAdjacentHTML('beforeend', renderToastContainer());
    }
}

// Export für Module (falls benötigt)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initComponents, renderSidebar, renderHeader, renderApiKeyModal, renderToastContainer };
}
