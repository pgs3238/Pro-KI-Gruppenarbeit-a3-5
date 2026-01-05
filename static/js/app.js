// ==================== KONFIGURATION ====================
const API_BASE_URL = 'http://localhost:8000';


// ==================== ACCOUNT BALANCE ====================

/**
 * Lädt den Kontogesamtbetrag von der API und zeigt ihn an
 */
async function loadKonten() {
    const totalBalance = document.getElementById('totalBalance');
    const kontenList = document.getElementById('kontenList');

    try {
        // API aufrufen: /transactions/stats/summary
        const response = await fetch(`${API_BASE_URL}/transactions/stats/summary`);
        const data = await response.json();
        
        // Saldo in der Website anzeigen
        if (totalBalance) {
            totalBalance.textContent = data.balance.toFixed(2).replace('.', ',') + '€';
        }
        
        // Konten-Liste clearen (später könnten wir hier einzelne Konten anzeigen)
        if (kontenList) {
            kontenList.innerHTML = '';
        }
        
        console.log('✓ Balance geladen von API:', data.balance + '€');
        return data;
    } catch (error) {
        console.error('✗ Fehler beim Laden des Saldos:', error);
        if (totalBalance) {
            totalBalance.textContent = '0,00€';
        }
    }
}


// ==================== CHART ====================

/**
 * Erstellt das Balance-Diagramm (Einnahmen vs Ausgaben)
 */
function createBalanceChart() {
    const chartElement = document.getElementById('balanceChart');
    if (!chartElement) return; // Abbrechen wenn Element nicht existiert
    
    const ctx = chartElement.getContext('2d');

    // Berechne die letzten 6 Monate
    const monthNames = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
    const today = new Date();
    const last6Months = [];

    for (let i = 5; i >= 0; i--) {
        const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
        last6Months.push(monthNames[date.getMonth()]);
    }

    // Beispieldaten für das Diagramm
    const data = {
        labels: last6Months,
        datasets: [
            {
                label: 'Einnahmen',
                data: [3000, 2800, 3200, 3100, 3500, 3200],
                backgroundColor: '#06d6a6',
                borderColor: '#06d6a6',
                borderWidth: 1,
                borderRadius: 5
            },
            {
                label: 'Ausgaben',
                data: [1200, 1350, 1100, 1450, 1300, 1400],
                backgroundColor: '#fff',
                borderColor: '#fff',
                borderWidth: 1,
                borderRadius: 5
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom',
                align: 'start',
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


// ==================== NAVIGATION ====================

/**
 * Setzt die Navigation Handler auf
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-link');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(i => i.classList.remove('active'));
            e.currentTarget.classList.add('active');
        });
    });
}


// ==================== SEARCH ====================

/**
 * Aktiviert die Suchfunktion
 */
function setupSearch() {
    const searchBox = document.getElementById('searchBox');
    if (!searchBox) return; // Abbrechen wenn Element nicht existiert
    
    const searchIcon = document.querySelector('.search-icon');

    // Icon verschwindet beim Tippen
    searchBox.addEventListener('input', (e) => {
        if (searchIcon) {
            searchIcon.style.display = e.target.value ? 'none' : 'block';
        }
    });

    // Filterfunktion
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#transactionsTable tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}


// ==================== TRANSACTIONS ====================

function loadTransactions() {
    console.log('Loading transactions...');
}


// ==================== PAGE INITIALIZATION ====================

/**
 * Lädt alle Daten wenn die Seite geladen ist
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Website geladen - lade Daten...');
    loadKonten();
    createBalanceChart();
    setupNavigation();
    setupSearch();
    loadTransactions();
});