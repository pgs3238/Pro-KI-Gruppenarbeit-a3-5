// ==================== KONFIGURATION ====================
// Nutzt API_BASE_URL aus utils.js
let availableKategorien = [];  // Cache für Kategorien
let availableKonten = [];      // Cache für Konten (global)


// ==================== KATEGORIEN LADEN ====================

async function loadKategorien() {
    try {
        availableKategorien = await fetchCategories();
        console.log('✓ Kategorien geladen:', availableKategorien);

        // Fülle alle Kategorie-Selects mit den geladenen Kategorien
        updateKategorieSelects();

        return availableKategorien;
    } catch (error) {
        console.error('✗ Fehler beim Laden der Kategorien:', error);
        return [];
    }
}

function updateKategorieSelects() {
    const selects = document.querySelectorAll('select[name="kategorie"]');

    selects.forEach(select => {
        // Merke aktuellen Wert
        const currentValue = select.value;

        // Speichere nur die erste Option "Bitte wählen..."
        const firstOption = select.options[0];
        const firstOptionValue = firstOption.value;
        const firstOptionText = firstOption.text;

        // Leere das Select komplett
        select.innerHTML = '';

        // Füge das "Bitte wählen..." wieder hinzu
        const emptyOption = document.createElement('option');
        emptyOption.value = firstOptionValue;
        emptyOption.text = firstOptionText;
        select.appendChild(emptyOption);

        // Gruppiere nach Typ
        const ausgaben = availableKategorien.filter(k => k.category_type === 'Ausgabe');
        const einnahmen = availableKategorien.filter(k => k.category_type === 'Einnahme');

        // Füge Ausgaben hinzu
        if (ausgaben.length > 0) {
            const ausgabenGroup = document.createElement('optgroup');
            ausgabenGroup.label = 'Ausgaben';
            ausgaben.forEach(kat => {
                const option = document.createElement('option');
                option.value = kat.id;
                option.text = `${kat.icon} ${kat.name}`;
                ausgabenGroup.appendChild(option);
            });
            select.appendChild(ausgabenGroup);
        }

        // Füge Einnahmen hinzu
        if (einnahmen.length > 0) {
            const einnahmenGroup = document.createElement('optgroup');
            einnahmenGroup.label = 'Einnahmen';
            einnahmen.forEach(kat => {
                const option = document.createElement('option');
                option.value = kat.id;
                option.text = `${kat.icon} ${kat.name}`;
                einnahmenGroup.appendChild(option);
            });
            select.appendChild(einnahmenGroup);
        }

        // Stelle den vorherigen Wert wieder her (falls vorhanden)
        if (currentValue) {
            select.value = currentValue;
        }
    });
}


// ==================== ACCOUNT BALANCE ====================

/**
 * Lädt den Kontogesamtbetrag von der API und zeigt ihn an
 */
async function loadKonten() {
    const totalBalance = document.getElementById('totalBalance');
    const kontenList = document.getElementById('kontenList');

    try {
        // Lade zuerst die verfügbaren Konten
        const konten = await fetchKonten();
        availableKonten = konten;  // Speichere die Konten für Lookups
        console.log('✓ Konten geladen:', konten);

        // Lade den aktuellen Saldo für ALLE Konten
        let totalSaldo = 0;
        const kontenMitSaldo = [];

        for (let konto of konten) {
            try {
                const saldoData = await fetchKontoSaldo(konto.id);
                totalSaldo += saldoData.aktueller_saldo;
                kontenMitSaldo.push({
                    ...konto,
                    saldo: saldoData.aktueller_saldo
                });
                console.log(`✓ Saldo für ${konto.kontoname}: ${saldoData.aktueller_saldo}€`);
            } catch (error) {
                console.warn(`Fehler beim Laden des Saldos für Konto ${konto.id}:`, error);
            }
        }

        // Saldo in der Website anzeigen
        if (totalBalance) {
            totalBalance.textContent = totalSaldo.toFixed(2).replace('.', ',') + '€';
        }

        // Konten-Liste clearen (später könnten wir hier einzelne Konten anzeigen)
        if (kontenList) {
            kontenList.innerHTML = '';
        }

        console.log('✓ Gesamtsaldo aller Konten:', totalSaldo.toFixed(2) + '€');
        return { balance: totalSaldo };
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
    const today = new Date();
    const last6Months = [];

    for (let i = 5; i >= 0; i--) {
        const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
        last6Months.push(MONTH_NAMES_DE_SHORT[date.getMonth()]);
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


// ==================== SANKEY DIAGRAMM ====================

/**
 * Lädt und erstellt das Sankey-Diagramm
 */
async function createSankeyChart() {
    const sankeyElement = document.getElementById('sankeyChart');
    if (!sankeyElement) return; // Abbrechen wenn Element nicht existiert

    try {
        // Lade Sankey-Daten von der API
        const response = await fetch(`${API_BASE_URL}/transactions/sankey-data`);
        const data = await response.json();

        if (!data.nodes || data.nodes.length === 0) {
            sankeyElement.innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">Keine Daten verfügbar</div>';
            return;
        }

        // Prepare data for Plotly
        const nodeNames = data.nodes.map(n => n.name);
        const nodeColors = data.nodes.map(n => n.color || '#1f77b4');

        const trace = {
            type: "sankey",
            node: {
                pad: 15,
                thickness: 20,
                line: {
                    color: "black",
                    width: 0.5
                },
                label: nodeNames,
                color: nodeColors
            },
            link: {
                source: data.links.map(l => l.source),
                target: data.links.map(l => l.target),
                value: data.links.map(l => l.value)
            }
        };

        const layout = {
            title: {
                text: "Geldfluss nach Kategorien",
                font: { color: "#ccc", size: 16 }
            },
            font: {
                size: 12,
                color: "#888"
            },
            plot_bgcolor: "transparent",
            paper_bgcolor: "#222",
            margin: { l: 50, r: 50, t: 50, b: 50 }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(sankeyElement, [trace], layout, config);
        console.log('✓ Sankey-Diagramm geladen');
    } catch (error) {
        console.error('✗ Fehler beim Laden des Sankey-Diagramms:', error);
        sankeyElement.innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">Fehler beim Laden des Diagramms</div>';
    }
}


// ==================== FAB MENU ====================

/**
 * Schaltet das FAB-Menü (Floating Action Button) ein/aus
 */
function toggleFabMenu() {
    const fabMenu = document.getElementById('fabMenu');
    const fabBtn = document.querySelector('.fab-btn');

    if (fabMenu.style.display === 'none') {
        fabMenu.style.display = 'flex';
        fabBtn.innerHTML = '×';
        fabBtn.classList.add('active');
    } else {
        fabMenu.style.display = 'none';
        fabBtn.innerHTML = '+';
        fabBtn.classList.remove('active');
    }
}


// ==================== PAGE INITIALIZATION ====================

/**
 * Lädt alle Daten wenn die Seite geladen ist (konsolidierter Handler)
 */
document.addEventListener('DOMContentLoaded', async function () {
    console.log('📱 Website geladen - lade Daten...');

    // Lade Kategorien für alle Seiten
    await loadKategorien();

    // Lade Konten
    await loadKonten();

    // Setup alle Handler
    setupNavigation();
    setupSearch();
    setupFilterInputs();
    setupTransactionModal();
    setupImportForm();

    // Seiten-spezifische Initialisierung
    if (document.getElementById('transactionsTable')) {
        await loadTransactions();
    }

    // Dashboard-spezifische Charts
    if (document.getElementById('balanceChart')) {
        createBalanceChart();
    }
    if (document.getElementById('sankeyChart')) {
        createSankeyChart();
    }
});
