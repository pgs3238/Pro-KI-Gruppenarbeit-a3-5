// ==================== MODAL FUNKTIONEN ====================
function openModal() {
    const modal = document.getElementById('transactionModal');
    if (!modal) return;

    modal.classList.add('active');
    setCurrentDate();
    loadKontoSelect();  // Lade Konten in das Dropdown
}

// Modal schließen
function closeModal() {
    const modal = document.getElementById('transactionModal');
    if (!modal) return;

    modal.classList.remove('active');
    // Formular zurücksetzen
    document.getElementById('transactionForm').reset();
    document.querySelector('.modal-title').textContent = 'Transaktion erfassen';
    delete document.getElementById('transactionForm').dataset.editId;
}

// Import Modal öffnen
function openImportModal() {
    document.getElementById('importModal').classList.add('active');
    loadKontoSelect('importKontoSelect');
}

// Import Modal schließen
function closeImportModal() {
    document.getElementById('importModal').classList.remove('active');
}

// Lädt Konten in das Dropdown
async function loadKontoSelect(targetId = 'kontoSelect') {
    const kontoSelect = document.getElementById(targetId);
    if (!kontoSelect) return;

    try {
        const konten = await fetchKonten();
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
    } catch (error) {
        console.error('\u2717 Fehler beim Laden der Konten für Dropdown:', error);
        showToast('Fehler beim Laden der Konten', 'error');
    }
}

// Handler für Konto-Auswahl (z.B. IBAN Prefill)
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
    // Hinweis: Die automatische IBAN-Befüllung wurde entfernt, da sie nicht korrekt funktionierte
}

// Setup für Import-Formular
function setupImportForm() {
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
            console.error('\u2717 Import fehlgeschlagen:', error);
            showToast(`Import fehlgeschlagen: ${error.message}`, "error");
        }
    });
}

// Setup für Transaktions-Modal (Absenden, Zurücksetzen, Datumsvalidierung)
function setupTransactionModal() {
    const modal = document.getElementById('transactionModal');
    const datumInput = document.getElementById('datumInput');
    const transactionForm = document.getElementById('transactionForm');
    const selects = document.querySelectorAll('select.form-control');
    const ibanInput = document.querySelector('input[name="iban"]');

    if (!modal) return;

    // Datumsvariablen initialisieren
    if (!window.selectedDate) window.selectedDate = new Date();
    if (!window.currentMonth) window.currentMonth = new Date();

    // Modal-Klick-Handler
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Formular-Absende-Handler
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
            const kategorieId = document.querySelector('select[name="kategorie"]')?.value;
            const transactionData = {
                buchungstag: isoDate,
                beguenstigter: document.querySelector('input[name="beguenstigter"]')?.value || '',
                iban_kontonummer: (document.querySelector('input[name="iban"]')?.value || '').replace(/\s/g, ''),  // Entferne Leerzeichen
                verwendungszweck: document.querySelector('input[name="verwendungszweck"]')?.value || '',
                betrag: parseFloat(document.querySelector('input[name="betrag"]')?.value || 0),
                waehrung: 'EUR',
                konto_id: kontoId ? parseInt(kontoId) : null,
                kategorie_id: kategorieId ? parseInt(kategorieId) : null
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

        // Zurücksetzen-Handler
        transactionForm.addEventListener('reset', () => {
            setTimeout(() => {
                updateSelectEmptyClasses(selects);
            }, 0);
        });
    }

    // Datums-Eingabe-Handler
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

    // Kalender beim Klick außerhalb schließen
    document.addEventListener('click', (e) => {
        const calendar = document.getElementById('customCalendar');
        const dateWrapper = document.querySelector('.date-input-wrapper');
        if (dateWrapper && !dateWrapper.contains(e.target) && calendar?.style.display === 'block') {
            calendar.style.display = 'none';
        }
    });

    wireSelectEmptyClasses(selects);
}
