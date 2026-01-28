// ==================== TRANSAKTIONEN CRUD FUNKTIONEN ====================
/**
 * Lädt die Transaktionen von der API (formatiert vom Backend)
 */
async function loadTransactions() {
    const table = document.getElementById('transactionsTable');
    if (!table) return;

    table.innerHTML = '<tr><td colspan="8" style="text-align: center;">⏳ Laden...</td></tr>';

    try {
        // API aufrufen: GET /transactions/formatted/list
        const response = await fetch(`${API_BASE_URL}/transactions/formatted/list`, {
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

        // Zeige formatierte Transaktionen (vom Backend)
        transactions.forEach(t => {
            const row = table.insertRow();

            row.innerHTML = `
                <td>${t.datum}</td>
                <td>${t.beguenstigter}</td>
                <td>${t.iban}</td>
                <td>${t.konto}</td>
                <td>${t.verwendungszweck}</td>
                <td>${t.kategorie}</td>
                <td class="betrag-${t.betrag_class}">${t.betrag}</td>
                <td style="display: flex; gap: 8px;">
                    <button class="action-btn edit-btn" onclick="editTransaction(${t.id})" title="Bearbeiten">✏️</button>
                    <button class="action-btn delete-btn" onclick="deleteTransaction(${t.id})" title="Löschen">🗑️</button>
                </td>
            `;
        });

        console.log('✓ ' + transactions.length + ' Transaktionen geladen');
    } catch (error) {
        console.error('✗ Fehler beim Laden:', error);
        table.innerHTML = `<tr><td colspan="8" style="text-align: center; color: red;">❌ Fehler: ${error.message}</td></tr>`;
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
        const germanDate = formatDateDE(date, { pad: true });

        // Speichere Datum-Informationen
        window.selectedDate = date;
        window.currentMonth = new Date(date);

        // Formular mit Daten befüllen (außer Konto - das kommt nach dem Modal-Öffnen)
        document.querySelector('input[name="datum"]').value = germanDate;
        document.querySelector('input[name="beguenstigter"]').value = transaction.beguenstigter;
        document.querySelector('input[name="iban"]').value = transaction.iban_kontonummer || '';
        document.querySelector('input[name="verwendungszweck"]').value = transaction.verwendungszweck || '';
        document.querySelector('input[name="betrag"]').value = transaction.betrag;

        // Kategorie setzen - nutze kategorie_id falls vorhanden
        if (transaction.kategorie_id) {
            document.querySelector('select[name="kategorie"]').value = transaction.kategorie_id;
        } else {
            document.querySelector('select[name="kategorie"]').value = '';
        }

        // Modal-Titel ändern und ID speichern
        document.querySelector('.modal-title').textContent = 'Transaktion bearbeiten';
        document.getElementById('transactionForm').dataset.editId = id;

        openModal();

        // Konto nach kurzer Verzögerung setzen (Dropdown wird erst im Modal geladen)
        if (transaction.konto_id) {
            setTimeout(() => {
                document.querySelector('select[name="konto_id"]').value = transaction.konto_id;
            }, 200);
        }
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
