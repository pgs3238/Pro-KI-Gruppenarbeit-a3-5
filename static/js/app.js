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
        // Lade zuerst die verfügbaren Konten
        const kontenResponse = await fetch(`${API_BASE_URL}/konten`);
        if (!kontenResponse.ok) throw new Error('Fehler beim Laden der Konten');
        
        const konten = await kontenResponse.json();
        availableKonten = konten;  // Speichere die Konten für Lookups
        console.log('✓ Konten geladen:', konten);
        
        // Lade den aktuellen Saldo für ALLE Konten
        let totalSaldo = 0;
        const kontenMitSaldo = [];
        
        for (let konto of konten) {
            try {
                const saldoResponse = await fetch(`${API_BASE_URL}/konten/${konto.id}/saldo`);
                if (saldoResponse.ok) {
                    const saldoData = await saldoResponse.json();
                    totalSaldo += saldoData.aktueller_saldo;
                    kontenMitSaldo.push({
                        ...konto,
                        saldo: saldoData.aktueller_saldo
                    });
                    console.log(`✓ Saldo für ${konto.kontoname}: ${saldoData.aktueller_saldo}€`);
                }
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
// ==================== SEARCH ====================

/**
 * Aktiviert die Suchfunktion
 */
function setupSearch() {
    const searchBox = document.getElementById('searchBox');
    if (!searchBox) return; // Abbrechen wenn Element nicht existiert
    
    const searchIcon = document.querySelector('.search-icon');

    
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


// ==================== SEARCH ====================
function setupFilterInputs() {
    const filterInputs = document.querySelectorAll('.filter-input');
    
    filterInputs.forEach((input, index) => {
        input.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                await performSearch();
            }
        });
    });
}


/**
 * Führt die Suche basierend auf Filter-Inputs durch
 */
async function performSearch() {
    const table = document.getElementById('transactionsTable');
    if (!table) return;

    // Sammle alle Filter-Werte
    const filterInputs = document.querySelectorAll('.filter-input');
    
    const searchParams = {
        buchungstag: filterInputs[0].value || null,
        beguenstigter: filterInputs[1].value || null,
        iban_kontonummer: filterInputs[2].value || null,
        verwendungszweck: filterInputs[4].value || null,
        beschreibung: filterInputs[5].value || null,
        betrag_str: filterInputs[6].value || null
    };

    table.innerHTML = '<tr><td colspan="7" style="text-align: center;">⏳ Suche läuft...</td></tr>';

    try {
        // Baue den Request Body
        const requestBody = {};
        
        if (searchParams.buchungstag) {
            requestBody.buchungstag = searchParams.buchungstag;
        }
        if (searchParams.beguenstigter) {
            requestBody.beguenstigter = searchParams.beguenstigter;
        }
        if (searchParams.iban_kontonummer) {
            requestBody.iban_kontonummer = searchParams.iban_kontonummer;
        }
        if (searchParams.verwendungszweck) {
            requestBody.verwendungszweck = searchParams.verwendungszweck;
        }
        if (searchParams.betrag_str) {
            const betrag = parseFloat(searchParams.betrag_str);
            if (!isNaN(betrag)) {
                requestBody.betrag_min = betrag;
                requestBody.betrag_max = betrag;
            }
        }

        // API aufrufen: POST /transactions/search
        const response = await fetch(`${API_BASE_URL}/transactions/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`API-Fehler: ${response.status}`);
        }

        const transactions = await response.json();
        
        table.innerHTML = '';

        if (transactions.length === 0) {
            table.innerHTML = '<tr><td colspan="7" style="text-align: center;">Keine Transaktionen gefunden</td></tr>';
            return;
        }

        // Zeige Suchergebnisse an
        transactions.forEach(t => {
            const row = table.insertRow();
            const betragClass = t.betrag >= 0 ? 'betrag-positiv' : 'betrag-negativ';
            const betragText = (t.betrag >= 0 ? '+' : '') + t.betrag.toFixed(2).replace('.', ',') + '€';
            
            const date = new Date(t.buchungstag);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const formattedDate = `${day}.${month}.${year}`;
            
            const kategorie = t.beschreibung ? t.beschreibung.charAt(0).toUpperCase() + t.beschreibung.slice(1) : '-';

            row.innerHTML = `
                <td>${formattedDate}</td>
                <td>${t.beguenstigter}</td>
                <td>${t.iban_kontonummer ? formatIBAN(t.iban_kontonummer) : '-'}</td>
                <td>${t.verwendungszweck || '-'}</td>
                <td>${kategorie}</td>
                <td class="${betragClass}">${betragText}</td>
                <td style="display: flex; gap: 8px;">
                    <button class="action-btn edit-btn" onclick="editTransaction(${t.id})" title="Bearbeiten">✏️</button>
                    <button class="action-btn delete-btn" onclick="deleteTransaction(${t.id})" title="Löschen">🗑️</button>
                </td>
            `;
        });

        console.log('✓ Suchergebnisse:', transactions.length);
    } catch (error) {
        console.error('✗ Fehler bei der Suche:', error);
        table.innerHTML = `<tr><td colspan="7" style="text-align: center; color: red;">Fehler bei der Suche</td></tr>`;
    }
}





// ==================== PAGE INITIALIZATION ====================

/**
 * Lädt alle Daten wenn die Seite geladen ist
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📱 Website geladen - lade Daten...');
    await loadKonten();  // Warte bis Konten geladen sind
    createBalanceChart();
    createSankeyChart();
    setupNavigation();
    setupSearch();
    setupFilterInputs();
    loadTransactions();
    setupTransactionModal();
});


// ==================== TRANSACTIONS (transactions.html) ====================

/**
 * Lädt die letzten 30 Transaktionen von der API und zeigt sie in der Tabelle
 */
async function loadTransactions() {
    const table = document.getElementById('transactionsTable');
    if (!table) return;
    
    table.innerHTML = '<tr><td colspan="8" style="text-align: center;">⏳ Laden...</td></tr>';

    try {
        // API aufrufen: GET /transactions?limit=30
        const response = await fetch(`${API_BASE_URL}/transactions?limit=30`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`API-Fehler: ${response.status}`);
        }

        const transactions = await response.json();
        
        table.innerHTML = '';

        if (transactions.length === 0) {
            table.innerHTML = '<tr><td colspan="8" style="text-align: center;">Keine Transaktionen gefunden</td></tr>';
            return;
        }

        // Umgekehrte Reihenfolge (neueste zuerst)
        transactions.reverse().forEach(t => {
            const row = table.insertRow();
            const betragClass = t.betrag >= 0 ? 'betrag-positiv' : 'betrag-negativ';
            const betragText = (t.betrag >= 0 ? '+' : '') + t.betrag.toFixed(2).replace('.', ',') + '€';
            
            // Formatiere Datum als dd.mm.yyyy
            const date = new Date(t.buchungstag);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const formattedDate = `${day}.${month}.${year}`;
            
            // Kategorie mit großem Anfangsbuchstaben
            const kategorie = t.beschreibung ? t.beschreibung.charAt(0).toUpperCase() + t.beschreibung.slice(1) : '-';
            
            // Suche das zugehörige Konto
            const konto = t.konto_id ? availableKonten.find(k => k.id === t.konto_id) : null;
            const kontoName = konto ? konto.kontoname : '-';
            
            console.log(`DEBUG Transaction: id=${t.id}, konto_id=${t.konto_id}, availableKonten=${JSON.stringify(availableKonten)}, kontoName=${kontoName}`);

            row.innerHTML = `
                <td>${formattedDate}</td>
                <td>${t.beguenstigter}</td>
                <td>${t.iban_kontonummer ? formatIBAN(t.iban_kontonummer) : '-'}</td>
                <td>${kontoName}</td>
                <td>${t.verwendungszweck || '-'}</td>
                <td>${kategorie}</td>
                <td class="${betragClass}">${betragText}</td>
                <td style="display: flex; gap: 8px;">
                    <button class="action-btn edit-btn" onclick="editTransaction(${t.id})" title="Bearbeiten">✏️</button>
                    <button class="action-btn delete-btn" onclick="deleteTransaction(${t.id})" title="Löschen">🗑️</button>
                </td>
            `;
        });

        console.log('✓ Transaktionen geladen:', transactions.length);
    } catch (error) {
        console.error('✗ Fehler beim Laden der Transaktionen:', error);
        table.innerHTML = `<tr><td colspan="8" style="text-align: center; color: red;">Fehler beim Laden der Transaktionen</td></tr>`;
    }
}

/**
 * Transaktion bearbeiten
 */
async function editTransaction(id) {
    try {
        // Lade Transaktion von der API
        const response = await fetch(`${API_BASE_URL}/transactions/${id}`);
        if (!response.ok) throw new Error('Transaktion nicht gefunden');
        
        const transaction = await response.json();

        // Konvertiere ISO Datum zu deutschem Format
        const date = new Date(transaction.buchungstag);
        const germanDate = `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`;
        
        // Speichere Datum-Informationen
        window.selectedDate = date;
        window.currentMonth = new Date(date);

        // Formular mit Daten befüllen
        document.querySelector('input[name="datum"]').value = germanDate;
        document.querySelector('input[name="beguenstigter"]').value = transaction.beguenstigter;
        document.querySelector('input[name="iban"]').value = transaction.iban_kontonummer || '';
        document.querySelector('input[name="verwendungszweck"]').value = transaction.verwendungszweck || '';
        document.querySelector('select[name="kategorie"]').value = transaction.beschreibung || '';
        document.querySelector('input[name="betrag"]').value = transaction.betrag;
        document.querySelector('select[name="konto_id"]').value = transaction.konto_id || '';

        // Modal-Titel ändern und ID speichern
        document.querySelector('.modal-title').textContent = 'Transaktion bearbeiten';
        document.getElementById('transactionForm').dataset.editId = id;

        openModal();
        
        // TODO ERROR remove this do to wrong function
        // Wenn ein Konto ausgewählt ist, trigger die onKontoSelect um IBAN zu befüllen
        // if (transaction.konto_id) {
        //     onKontoSelect();
        // }
    } catch (error) {
        console.error('✗ Fehler beim Laden der Transaktion:', error);
        showToast('Transaktion konnte nicht geladen werden', 'error');
    }
}

/**
 * Transaktion löschen
 */
async function deleteTransaction(id) {
    if (!confirm('Möchten Sie diese Transaktion wirklich löschen?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Fehler beim Löschen');

        showToast('Transaktion erfolgreich gelöscht!', 'success');
        loadTransactions();
        loadKonten();  // Auch die Kontostände neu laden
    } catch (error) {
        console.error('✗ Fehler beim Löschen der Transaktion:', error);
        showToast('Transaktion konnte nicht gelöscht werden', 'error');
    }
}

/**
 * Transaktionen importieren
 */
document.addEventListener("DOMContentLoaded", () => {
  const importForm = document.getElementById("importForm");
  if (!importForm) return;

  importForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();

    const inputs = importForm.querySelectorAll("input");
    const kontoSelect = importForm.querySelector("select");
    const fileInput = importForm.querySelector('input[type="file"]');

    formData.append("header_row", inputs[0].value);
    formData.append("skip_footer", inputs[6].value);

    const mapping = {
      buchungstag: inputs[1].value,
      beguenstigter: inputs[2].value,
      iban_kontonummer: inputs[3].value,
      verwendungszweck: inputs[4].value,
      betrag: inputs[5].value
    };

    formData.append("mapping", JSON.stringify(mapping));
    formData.append("konto_id", kontoSelect.value || "");
    formData.append("file", fileInput.files[0]);

    try {
      const response = await fetch(`${API_BASE_URL}/transactions/import`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMsg = errorData?.detail || errorData?.message || "Import fehlgeschlagen";
        throw new Error(errorMsg);
      }

      showToast("Import erfolgreich", "success");
      closeImportModal();
      loadTransactions();
      loadKonten();
    } catch (error) {
      console.error(error);
      showToast("Import fehlgeschlagen", "error");
    }
  });
});

/**
 * Speichert die verfügbaren Konten für Lookups
 */
let availableKonten = [];

/**
 * Lädt die verfügbaren Konten in das Konto-Dropdown
 */
async function loadKontoSelect(targetId = 'kontoSelect') {
    // const kontoSelect = document.getElementById('kontoSelect');
    const kontoSelect = document.getElementById(targetId);
    if (!kontoSelect) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/konten`);
        if (!response.ok) throw new Error('Fehler beim Laden der Konten');
        
        const konten = await response.json();
        availableKonten = konten;  // Speichere die Konten für Lookups
        
        // Behalte die erste leere Option
        kontoSelect.innerHTML = '<option value="">Kein Konto ausgewählt</option>';
        
        // Füge alle Konten als Optionen hinzu
        konten.forEach(konto => {
            const option = document.createElement('option');
            option.value = konto.id;
            option.textContent = `${konto.kontoname}`;
            kontoSelect.appendChild(option);
        });
        
        // TODO Error remove this due to wrong function
        // Füge Change-Event hinzu, um IBAN automatisch zu füllen
        // if (targetId === 'kontoSelect') {
        //     kontoSelect.addEventListener('change', onKontoSelect);
        // }
    } catch (error) {
        console.error('Fehler beim Laden der Konten für Dropdown:', error);
    }
}

/**
 * Event Handler: Wenn Konto ausgewählt wird, IBAN automatisch eintragen
 */
function onKontoSelect() {
    const kontoSelect = document.getElementById('kontoSelect');
    const ibanInput = document.querySelector('input[name="iban"]');
    
    if (!kontoSelect || !ibanInput) return;
    
    const selectedKontoId = parseInt(kontoSelect.value);
    
    if (!selectedKontoId) {
        // Kein Konto ausgewählt - IBAN-Feld leeren und editierbar machen
        ibanInput.value = '';
        ibanInput.readOnly = false;
        ibanInput.style.backgroundColor = '';  // Standardfarbe
        return;
    }
    
    // Finde das ausgewählte Konto
    const selectedKonto = availableKonten.find(k => k.id === selectedKontoId);
    

    // TODO remove function due to it doing the wrong thing!!
    // if (selectedKonto && selectedKonto.kontonummer) {
    //     // Trage die IBAN des Kontos ein
    //     ibanInput.value = selectedKonto.kontonummer;
    //     // Mache IBAN-Feld readonly
    //     ibanInput.readOnly = true;
    //     ibanInput.style.backgroundColor = '#333';  // Dunkler Hintergrund für readonly
    // }
}

/**
 * Modal öffnen
 */
function openModal() {
    const modal = document.getElementById('transactionModal');
    if (!modal) return;
    
    modal.classList.add('active');
    setCurrentDate();
    loadKontoSelect();  // Lade Konten in das Dropdown
}

/**
 * Modal schließen
 */
function closeModal() {
    const modal = document.getElementById('transactionModal');
    if (!modal) return;
    
    modal.classList.remove('active');
    // Formular zurücksetzen
    document.getElementById('transactionForm').reset();
    document.querySelector('.modal-title').textContent = 'Transaktion erfassen';
    delete document.getElementById('transactionForm').dataset.editId;
}


/**
 *  
 */
function openImportModal() {
    document.getElementById('importModal').classList.add('active');
    loadKontoSelect('importKontoSelect');
}

/**
 * 
 */
function closeImportModal() {
    document.getElementById('importModal').classList.remove('active');
}



/**
 * Setze aktuelles Datum als Standardwert
 */
function setCurrentDate() {
    const datumInput = document.getElementById('datumInput');
    if (!datumInput) return;
    
    const today = new Date();
    window.selectedDate = today;
    window.currentMonth = new Date(today);
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    datumInput.value = `${day}.${month}.${year}`;
}

/**
 * Calendar Toggle
 */
function toggleCalendar() {
    const calendar = document.getElementById('customCalendar');
    if (!calendar) return;
    calendar.style.display = calendar.style.display === 'none' ? 'block' : 'none';
    if (calendar.style.display === 'block') {
        renderCalendar();
    }
}

/**
 * Wechsel Monat im Kalender
 */
function changeMonth(direction) {
    if (!window.currentMonth) window.currentMonth = new Date();
    window.currentMonth.setMonth(window.currentMonth.getMonth() + direction);
    renderCalendar();
}

/**
 * Rendere Kalender
 */
function renderCalendar() {
    if (!window.currentMonth) window.currentMonth = new Date();
    
    const year = window.currentMonth.getFullYear();
    const month = window.currentMonth.getMonth();
    
    // Update header
    const monthNames = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                       'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
    const monthYear = document.getElementById('calendarMonthYear');
    if (monthYear) monthYear.textContent = `${monthNames[month]} ${year}`;
    
    // Calculate days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;
    
    const calendarDays = document.getElementById('calendarDays');
    if (!calendarDays) return;
    
    calendarDays.innerHTML = '';
    
    // Empty cells for days before month starts
    for (let i = 0; i < adjustedFirstDay; i++) {
        calendarDays.innerHTML += '<span class="calendar-day empty"></span>';
    }
    
    // Days of month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        const isSelected = day === (window.selectedDate?.getDate?.()) && month === window.selectedDate?.getMonth?.() && year === window.selectedDate?.getFullYear?.();
        const classes = `calendar-day${isToday ? ' today' : ''}${isSelected ? ' selected' : ''}`;
        calendarDays.innerHTML += `<span class="${classes}" onclick="selectDate(${day})">${day}</span>`;
    }
}

/**
 * Wähle Datum im Kalender
 */
function selectDate(day) {
    if (!window.currentMonth) window.currentMonth = new Date();
    window.selectedDate = new Date(window.currentMonth.getFullYear(), window.currentMonth.getMonth(), day);
    const formattedDate = `${String(day).padStart(2, '0')}.${String(window.currentMonth.getMonth() + 1).padStart(2, '0')}.${window.currentMonth.getFullYear()}`;
    const datumInput = document.getElementById('datumInput');
    if (datumInput) datumInput.value = formattedDate;
    const calendar = document.getElementById('customCalendar');
    if (calendar) calendar.style.display = 'none';
}

/**
 * Richte Transaction Modal Setup ein
 */
function setupTransactionModal() {
    const modal = document.getElementById('transactionModal');
    const datumInput = document.getElementById('datumInput');
    const transactionForm = document.getElementById('transactionForm');
    const selects = document.querySelectorAll('select.form-control');
    const ibanInput = document.querySelector('input[name="iban"]');
    
    if (!modal) return;
    
    // Initialize date variables
    if (!window.selectedDate) window.selectedDate = new Date();
    if (!window.currentMonth) window.currentMonth = new Date();

    // Modal click handler
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Form submit handler
    if (transactionForm) {
        transactionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const editId = form.dataset.editId;

            // Konvertiere deutsches Datum zu ISO Format
            const datumParts = (datumInput?.value || '').split('.');
            const isoDate = `${datumParts[2]}-${datumParts[1]}-${datumParts[0]}`;

            // Formulardaten auslesen
            const kontoId = document.querySelector('select[name="konto_id"]')?.value;
            const transactionData = {
                buchungstag: isoDate,
                beguenstigter: document.querySelector('input[name="beguenstigter"]')?.value || '',
                iban_kontonummer: (document.querySelector('input[name="iban"]')?.value || '').replace(/\s/g, ''),  // Entferne Leerzeichen
                verwendungszweck: document.querySelector('input[name="verwendungszweck"]')?.value || '',
                beschreibung: document.querySelector('select[name="kategorie"]')?.value || '',
                betrag: parseFloat(document.querySelector('input[name="betrag"]')?.value || 0),
                waehrung: 'EUR',
                konto_id: kontoId ? parseInt(kontoId) : null
            };

            try {
                if (editId) {
                    // Bestehende Transaktion aktualisieren
                    const response = await fetch(`${API_BASE_URL}/transactions/${editId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(transactionData)
                    });

                    if (!response.ok) throw new Error('Fehler beim Aktualisieren');
                    showToast('Transaktion erfolgreich aktualisiert!', 'success');
                } else {
                    // Neue Transaktion hinzufügen
                    const response = await fetch(`${API_BASE_URL}/transactions`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(transactionData)
                    });

                    if (!response.ok) throw new Error('Fehler beim Speichern');
                    showToast('Transaktion erfolgreich gespeichert!', 'success');
                }

                loadTransactions();
                loadKonten();  // Auch die Kontostände neu laden
                closeModal();
            } catch (error) {
                console.error('✗ Fehler bei der Transaktion:', error);
                showToast('Fehler beim Speichern der Transaktion: ' + error.message, 'error');
            }
        });

        // Reset handler
        transactionForm.addEventListener('reset', () => {
            setTimeout(() => {
                selects.forEach(select => updateSelectColor(select));
            }, 0);
        });
    }

    // Datum Input Handler
    if (datumInput) {
        datumInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.slice(0, 2) + '.' + value.slice(2);
            }
            if (value.length >= 5) {
                value = value.slice(0, 5) + '.' + value.slice(5, 9);
            }
            e.target.value = value;
        });

        datumInput.addEventListener('blur', (e) => {
            const value = e.target.value;
            const dateRegex = /^(\d{2})\.(\d{2})\.(\d{4})$/;
            const match = value.match(dateRegex);
            
            if (match) {
                const day = parseInt(match[1]);
                const month = parseInt(match[2]);
                const year = parseInt(match[3]);
                
                const date = new Date(year, month - 1, day);
                if (date.getDate() === day && date.getMonth() === month - 1 && date.getFullYear() === year) {
                    window.selectedDate = date;
                    window.currentMonth = new Date(date);
                } else {
                    e.target.setCustomValidity('Bitte geben Sie ein gültiges Datum ein.');
                }
            }
        });

        datumInput.addEventListener('input', () => {
            datumInput.setCustomValidity('');
        });

        datumInput.addEventListener('focus', (e) => {
            e.target.select();
        });

        datumInput.addEventListener('click', (e) => {
            e.target.select();
        });
    }

    // Close calendar on outside click
    document.addEventListener('click', (e) => {
        const calendar = document.getElementById('customCalendar');
        const dateWrapper = document.querySelector('.date-input-wrapper');
        if (dateWrapper && !dateWrapper.contains(e.target) && calendar?.style.display === 'block') {
            calendar.style.display = 'none';
        }
    });

    // Select color update handler
    function updateSelectColor(select) {
        if (select.value === "") {
            select.classList.add('empty');
        } else {
            select.classList.remove('empty');
        }
    }

    selects.forEach(select => {
        updateSelectColor(select);
        select.addEventListener('change', () => updateSelectColor(select));
    });
}