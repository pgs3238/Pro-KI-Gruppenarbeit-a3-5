// ==================== SUCH- UND FILTER-FUNKTIONEN ====================
// Aktiviert die einfache Textsuche für die Tabelle
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

// Setup Filter-Inputs für erweiterte Suche
function setupFilterInputs() {
    const filterInputs = document.querySelectorAll('.filter-input');
    const clearBtn = document.getElementById('clearFiltersBtn');

    // Suche nur bei Enter-Taste
    filterInputs.forEach((input) => {
        input.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                console.log('📍 Enter gedrückt - starte Suche');
                await performSearch();
            }
        });
    });

    // Zurücksetzen-Button Setup
    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            // Alle Filter leeren
            filterInputs.forEach(input => {
                input.value = '';
            });
            // Alle Transaktionen laden
            await loadTransactions();
            console.log('✓ Filter gelöscht - zeige alle Transaktionen');
        });
    }
}

// Führt erweiterte Suche via API durch
async function performSearch() {
    const table = document.getElementById('transactionsTable');
    if (!table) return;

    // Sammle alle Filter-Werte über data-Attribute
    const filterInputs = document.querySelectorAll('.filter-input');

    const searchParams = {};
    filterInputs.forEach(input => {
        const filterName = input.getAttribute('data-filter');
        if (filterName && input.value.trim()) {
            searchParams[filterName] = input.value.trim();
        }
    });

    // Wenn keine Filter gesetzt sind, zeige Nachricht
    if (Object.keys(searchParams).length === 0) {
        console.log('ℹ️ Keine Filter gesetzt - zeige alle Transaktionen');
        await loadTransactions();
        return;
    }

    table.innerHTML = '<tr><td colspan="8" style="text-align: center;">⏳ Suche läuft...</td></tr>';

    try {
        // Baue den Request Body
        const requestBody = {};

        if (searchParams.buchungstag) {
            // Validiere das Datumsformat (TT.MM.JJJJ oder TT-MM-JJJJ)
            const dateRegex = /^\d{2}[.-]\d{2}[.-]\d{4}$/;
            if (!dateRegex.test(searchParams.buchungstag)) {
                throw new Error('❌ Ungültiges Datumsformat. Bitte nutze das Format TT.MM.JJJJ oder TT-MM-JJJJ');
            }
            // Konvertiere TT.MM.JJJJ oder TT-MM-JJJJ → YYYY-MM-DD
            const parts = searchParams.buchungstag.split(/[.-]/);
            const isoDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
            requestBody.buchungstag = isoDate;
        }

        if (searchParams.beguenstigter) {
            requestBody.beguenstigter = searchParams.beguenstigter;
        }
        if (searchParams.iban_kontonummer) {
            requestBody.iban_kontonummer = searchParams.iban_kontonummer;
        }
        if (searchParams.konto_name) {
            requestBody.konto_name = searchParams.konto_name;
        }
        if (searchParams.verwendungszweck) {
            requestBody.verwendungszweck = searchParams.verwendungszweck;
        }
        if (searchParams.kategorie_name) {
            requestBody.kategorie_name = searchParams.kategorie_name;
        }
        if (searchParams.beschreibung) {
            requestBody.beschreibung = searchParams.beschreibung;
        }
        if (searchParams.betrag_min) {
            const betragMin = parseFloat(searchParams.betrag_min.replace(',', '.'));
            if (!isNaN(betragMin)) {
                requestBody.betrag_min_abs = betragMin;
            }
        }
        if (searchParams.betrag_max) {
            const betragMax = parseFloat(searchParams.betrag_max.replace(',', '.'));
            if (!isNaN(betragMax)) {
                requestBody.betrag_max_abs = betragMax;
            }
        }

        console.log("📤 Suchparameter:", searchParams);
        console.log("📤 Sende Suche an API:", requestBody);

        // API aufrufen: POST /transactions/search
        const response = await fetch(`${API_BASE_URL}/transactions/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`API-Fehler ${response.status}: ${errorData.detail || 'Unbekannter Fehler'}`);
        }

        const transactions = await response.json();

        table.innerHTML = '';

        if (transactions.length === 0) {
            table.innerHTML = '<tr><td colspan="8" style="text-align: center;">Keine Transaktionen gefunden</td></tr>';
            return;
        }

        // Zeige Suchergebnisse an
        transactions.forEach(t => {
            const row = table.insertRow();
            const betragClass = t.betrag >= 0 ? 'betrag-positiv' : 'betrag-negativ';
            const betragText = (t.betrag >= 0 ? '+' : '') + t.betrag.toFixed(2).replace('.', ',') + '€';
            const formattedDate = formatDateDE(t.buchungstag, { pad: true });

            //Konto Daten Suchen
            const konto = t.konto_id
                ? availableKonten.find(k => k.id === t.konto_id)
                : null;
            const kontoName = konto ? konto.kontoname : '-';

            // Kategorie über kategorie_id aus availableKategorien holen
            let kategorie = '-';
            if (t.kategorie_id) {
                const kat = availableKategorien.find(k => k.id === t.kategorie_id);
                kategorie = kat ? kat.name : '-';
            } else if (t.beschreibung) {
                // Fallback: beschreibung verwenden falls keine kategorie_id
                kategorie = t.beschreibung.charAt(0).toUpperCase() + t.beschreibung.slice(1);
            }

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

        console.log('✓ Suchergebnisse: ' + transactions.length + ' Transaktionen gefunden');
    } catch (error) {
        console.error('✗ Fehler bei der Suche:', error);
        table.innerHTML = `<tr><td colspan="8" style="text-align: center; color: red;">❌ Fehler: ${error.message}</td></tr>`;
    }
}
