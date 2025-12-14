// ============ BEISPIELDATEN (SPÄTER DURCH API ERSETZEN) ============
// Diese Daten werden später durch echte API-Aufrufe ersetzt
const exampleData = {
    transactions: [
        {
            id: 1,
            buchungstag: '2025-12-14',
            beguenstigter: 'Amazon',
            verwendungszweck: 'Online Shopping',
            betrag: -29.99,
            waehrung: 'EUR'
        },
        {
            id: 2,
            buchungstag: '2025-12-13',
            beguenstigter: 'Gehalt',
            verwendungszweck: 'Dezember Einkommen',
            betrag: 2500.00,
            waehrung: 'EUR'
        },
        {
            id: 3,
            buchungstag: '2025-12-12',
            beguenstigter: 'Edeka',
            verwendungszweck: 'Lebensmittel',
            betrag: -45.67,
            waehrung: 'EUR'
        },
        {
            id: 4,
            buchungstag: '2025-12-11',
            beguenstigter: 'Netflix',
            verwendungszweck: 'Abo',
            betrag: -12.99,
            waehrung: 'EUR'
        },
        {
            id: 5,
            buchungstag: '2025-12-10',
            beguenstigter: 'DKB Bank',
            verwendungszweck: 'Zinsen',
            betrag: 5.00,
            waehrung: 'EUR'
        }
    ],
    konten: {
        'Konto 1': 1500.00,
        'Konto 2': 3000.00,
        'Konto 3': 4500.00
    }
};

// ============ FUNKTIONEN ============

/**
 * Lädt und zeigt die Konten mit ihren Salden an
 */
function loadKonten() {
    const kontenList = document.getElementById('kontenList');
    const totalBalance = document.getElementById('totalBalance');
    
    let total = 0;
    kontenList.innerHTML = '';

    // Iterate durch alle Konten und erstelle für jedes einen Eintrag
    for (const [kontoName, betrag] of Object.entries(exampleData.konten)) {
        total += betrag;
        const kontoItem = document.createElement('div');
        kontoItem.className = 'konto-item';
        kontoItem.innerHTML = `
            <div class="konto-label">${kontoName}</div>
            <div class="konto-betrag">${betrag.toFixed(2).replace('.', ',')}€</div>
        `;
        kontenList.appendChild(kontoItem);
    }

    // Zeige die Gesamtsumme an
    totalBalance.textContent = total.toFixed(2).replace('.', ',') + '€';
}

/**
 * Lädt und zeigt die Transaktionen in der Tabelle
 */
function loadTransactions() {
    const table = document.getElementById('transactionsTable');
    table.innerHTML = '';

    // Für jede Transaktion eine neue Zeile erstellen
    exampleData.transactions.forEach(t => {
        const row = table.insertRow();
        
        // Bestimme die CSS-Klasse basierend auf positiv/negativ
        const betragClass = t.betrag >= 0 ? 'betrag-positiv' : 'betrag-negativ';
        
        // Formatiere den Betrag mit + oder - und deutschem Format
        const betragText = (t.betrag >= 0 ? '+' : '') + t.betrag.toFixed(2).replace('.', ',') + '€';

        row.innerHTML = `
            <td>${new Date(t.buchungstag).toLocaleDateString('de-DE')}</td>
            <td>${t.beguenstigter}</td>
            <td>${t.verwendungszweck || '-'}</td>
            <td class="${betragClass}">${betragText}</td>
        `;
    });
}

/**
 * Erstellt das Balance-Diagramm mit Chart.js
 */
function createBalanceChart() {
    const ctx = document.getElementById('balanceChart').getContext('2d');
    
    // Beispieldaten für das Diagramm
    const data = {
        labels: ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul'],
        datasets: [
            {
                label: 'Einnahmen',
                data: [3000, 2800, 3200, 3100, 3500, 3200, 3800],
                backgroundColor: '#fff',
                borderColor: '#fff',
                borderWidth: 1,
                borderRadius: 5
            },
            {
                label: 'Ausgaben',
                data: [1200, 1350, 1100, 1450, 1300, 1400, 1250],
                backgroundColor: '#06d6a6',
                borderColor: '#06d6a6',
                borderWidth: 1,
                borderRadius: 5
            }
        ]
    };

    // Konfiguration für das Diagramm
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: '#ccc',
                    padding: 20,
                    usePointStyle: true
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    color: '#888'
                },
                grid: {
                    color: '#333',
                    drawBorder: false
                }
            },
            x: {
                ticks: {
                    color: '#888'
                },
                grid: {
                    color: 'transparent',
                    drawBorder: false
                }
            }
        }
    };

    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}

/**
 * Setup der Navigation - aktive Menüpunkte markieren
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-link');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Entferne active-Klasse von allen Elementen
            navItems.forEach(i => i.classList.remove('active'));
            // Füge active-Klasse zum geklickten Element hinzu
            e.currentTarget.classList.add('active');
        });
    });
}

/**
 * Suchfunktion - filtert Transaktionen live
 */
function setupSearch() {
    const searchBox = document.getElementById('searchBox');
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#transactionsTable tr');
        
        // Zeige/verstecke Reihen basierend auf Suchbegriff
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// ============ INITIALISIERUNG ============
// Warte bis die Seite vollständig geladen ist, dann initialisiere alles
document.addEventListener('DOMContentLoaded', () => {
    loadKonten();
    loadTransactions();
    createBalanceChart();
    setupNavigation();
    setupSearch();
});
