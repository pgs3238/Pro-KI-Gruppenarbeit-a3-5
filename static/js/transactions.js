// ============ BEISPIELDATEN ============
const exampleData = {
    transactions: [
        {
            id: 1,
            buchungstag: '2025-12-14',
            beguenstigter: 'Amazon',
            iban: 'DE89370400440532013000',
            verwendungszweck: 'Online Shopping',
            kategorie: 'Shopping',
            betrag: -29.99,
            waehrung: 'EUR'
        },
        {
            id: 2,
            buchungstag: '2025-12-13',
            beguenstigter: 'Gehalt',
            iban: 'DE75512108001245126199',
            verwendungszweck: 'Dezember Einkommen',
            kategorie: 'Gehalt',
            betrag: 2500.00,
            waehrung: 'EUR'
        },
        {
            id: 3,
            buchungstag: '2025-12-12',
            beguenstigter: 'Edeka',
            iban: 'DE44500105175407324931',
            verwendungszweck: 'Lebensmittel',
            kategorie: 'Lebensmittel',
            betrag: -45.67,
            waehrung: 'EUR'
        },
        {
            id: 4,
            buchungstag: '2025-12-11',
            beguenstigter: 'Netflix',
            iban: 'NL91ABNA0417164300',
            verwendungszweck: 'Abo',
            kategorie: 'Unterhaltung',
            betrag: -12.99,
            waehrung: 'EUR'
        },
        {
            id: 5,
            buchungstag: '2025-12-10',
            beguenstigter: 'DKB Bank',
            iban: 'DE12500105170648489890',
            verwendungszweck: 'Zinsen',
            kategorie: 'Zinsen',
            betrag: 5.00,
            waehrung: 'EUR'
        }
    ]
};

// Lädt und zeigt die Transaktionen in der Tabelle
function loadTransactions() {
    const table = document.getElementById('transactionsTable');
    table.innerHTML = '';

    exampleData.transactions.forEach(t => {
        const row = table.insertRow();
        const betragClass = t.betrag >= 0 ? 'betrag-positiv' : 'betrag-negativ';
        const betragText = (t.betrag >= 0 ? '+' : '') + t.betrag.toFixed(2).replace('.', ',') + '€';

        row.innerHTML = `
            <td>${new Date(t.buchungstag).toLocaleDateString('de-DE')}</td>
            <td>${t.beguenstigter}</td>
            <td>${t.iban || '-'}</td>
            <td>${t.verwendungszweck || '-'}</td>
            <td>${t.kategorie || '-'}</td>
            <td class="${betragClass}">${betragText}</td>
            <td>
                <button class="action-btn edit-btn" onclick="editTransaction(${t.id})" title="Bearbeiten">✏️</button>
                <button class="action-btn delete-btn" onclick="deleteTransaction(${t.id})" title="Löschen">🗑️</button>
            </td>
        `;
    });
}

// Transaktion bearbeiten
function editTransaction(id) {
    const transaction = exampleData.transactions.find(t => t.id === id);
    if (!transaction) return;

    // Konvertiere ISO Datum zu deutschem Format
    const date = new Date(transaction.buchungstag);
    const germanDate = `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`;
    selectedDate = date;
    currentMonth = new Date(date);

    // Formular mit Daten befüllen
    document.querySelector('input[name="datum"]').value = germanDate;
    document.querySelector('input[name="beguenstigter"]').value = transaction.beguenstigter;
    document.querySelector('input[name="iban"]').value = transaction.iban || '';
    document.querySelector('input[name="verwendungszweck"]').value = transaction.verwendungszweck || '';
    document.querySelector('select[name="kategorie"]').value = transaction.kategorie || '';
    document.querySelector('input[name="betrag"]').value = transaction.betrag;

    // Modal-Titel ändern und ID speichern
    document.querySelector('.modal-title').textContent = 'Transaktion bearbeiten';
    document.getElementById('transactionForm').dataset.editId = id;

    openModal();
}

// Transaktion löschen
function deleteTransaction(id) {
    if (confirm('Möchten Sie diese Transaktion wirklich löschen?')) {
        const index = exampleData.transactions.findIndex(t => t.id === id);
        if (index !== -1) {
            exampleData.transactions.splice(index, 1);
            loadTransactions();
            alert('Transaktion erfolgreich gelöscht!');
        }
    }
}

// Initial laden
document.addEventListener('DOMContentLoaded', () => {
    loadTransactions();

    // Einfache Interaktion für das Menü
    document.querySelectorAll('.nav-link').forEach(item => {
        item.addEventListener('click', (e) => {
            // Hier könnten wir Navigation simulieren
            if (item.id === 'nav-overview') window.location.href = 'index.html';
        });
    });

    // ============ MODAL LOGIC ============
    const modal = document.getElementById('transactionModal');
    const selects = document.querySelectorAll('select.form-control');
    const datumInput = document.getElementById('datumInput');
    selectedDate = new Date();
    currentMonth = new Date();

    // Custom Calendar Functions
    window.toggleCalendar = function() {
        const calendar = document.getElementById('customCalendar');
        calendar.style.display = calendar.style.display === 'none' ? 'block' : 'none';
        if (calendar.style.display === 'block') {
            renderCalendar();
        }
    };

    window.changeMonth = function(direction) {
        currentMonth.setMonth(currentMonth.getMonth() + direction);
        renderCalendar();
    };

    function renderCalendar() {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();
        
        // Update header
        const monthNames = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                           'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
        document.getElementById('calendarMonthYear').textContent = `${monthNames[month]} ${year}`;
        
        // Calculate days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1; // Adjust so Monday is 0
        
        const calendarDays = document.getElementById('calendarDays');
        calendarDays.innerHTML = '';
        
        // Empty cells for days before month starts
        for (let i = 0; i < adjustedFirstDay; i++) {
            calendarDays.innerHTML += '<span class="calendar-day empty"></span>';
        }
        
        // Days of month
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
            const isSelected = day === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear();
            const classes = `calendar-day${isToday ? ' today' : ''}${isSelected ? ' selected' : ''}`;
            calendarDays.innerHTML += `<span class="${classes}" onclick="selectDate(${day})">${day}</span>`;
        }
    }

    window.selectDate = function(day) {
        selectedDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
        const formattedDate = `${String(day).padStart(2, '0')}.${String(currentMonth.getMonth() + 1).padStart(2, '0')}.${currentMonth.getFullYear()}`;
        datumInput.value = formattedDate;
        document.getElementById('customCalendar').style.display = 'none';
    };

    // Setze aktuelles Datum als Standardwert
    function setCurrentDate() {
        const today = new Date();
        selectedDate = today;
        currentMonth = new Date(today);
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const year = today.getFullYear();
        datumInput.value = `${day}.${month}.${year}`;
    }

    // Schließe Kalender bei Klick außerhalb
    document.addEventListener('click', (e) => {
        const calendar = document.getElementById('customCalendar');
        const calendarIcon = document.querySelector('.calendar-icon');
        const dateWrapper = document.querySelector('.date-input-wrapper');
        if (dateWrapper && !dateWrapper.contains(e.target) && calendar.style.display === 'block') {
            calendar.style.display = 'none';
        }
    });

    // Automatische Formatierung bei manueller Eingabe
    datumInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, ''); // Nur Zahlen
        if (value.length >= 2) {
            value = value.slice(0, 2) + '.' + value.slice(2);
        }
        if (value.length >= 5) {
            value = value.slice(0, 5) + '.' + value.slice(5, 9);
        }
        e.target.value = value;
    });

    // Validierung bei Blur
    datumInput.addEventListener('blur', (e) => {
        const value = e.target.value;
        const dateRegex = /^(\d{2})\.(\d{2})\.(\d{4})$/;
        const match = value.match(dateRegex);
        
        if (match) {
            const day = parseInt(match[1]);
            const month = parseInt(match[2]);
            const year = parseInt(match[3]);
            
            // Prüfe gültiges Datum
            const date = new Date(year, month - 1, day);
            if (date.getDate() === day && date.getMonth() === month - 1 && date.getFullYear() === year) {
                selectedDate = date;
                currentMonth = new Date(date);
            } else {
                e.target.setCustomValidity('Bitte geben Sie ein gültiges Datum ein.');
            }
        }
    });

    datumInput.addEventListener('input', () => {
        datumInput.setCustomValidity('');
    });

    // Markiere gesamten Text beim Fokussieren
    datumInput.addEventListener('focus', (e) => {
        e.target.select();
    });

    datumInput.addEventListener('click', (e) => {
        e.target.select();
    });

    window.openModal = function() {
        modal.classList.add('active');
        setCurrentDate(); // Setze Datum beim Öffnen
    };

    window.closeModal = function() {
        modal.classList.remove('active');
        // Formular zurücksetzen
        document.getElementById('transactionForm').reset();
        document.querySelector('.modal-title').textContent = 'Transaktion erfassen';
        delete document.getElementById('transactionForm').dataset.editId;
    };

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    document.getElementById('transactionForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const form = e.target;
        const editId = form.dataset.editId;

        // Konvertiere deutsches Datum zu ISO Format
        const datumParts = document.querySelector('input[name="datum"]').value.split('.');
        const isoDate = `${datumParts[2]}-${datumParts[1]}-${datumParts[0]}`;

        // Formulardaten auslesen
        const transactionData = {
            buchungstag: isoDate,
            beguenstigter: document.querySelector('input[name="beguenstigter"]').value,
            iban: document.querySelector('input[name="iban"]').value,
            verwendungszweck: document.querySelector('input[name="verwendungszweck"]').value,
            kategorie: document.querySelector('select[name="kategorie"]').value,
            betrag: parseFloat(document.querySelector('input[name="betrag"]').value),
            waehrung: 'EUR'
        };

        if (editId) {
            // Bestehende Transaktion aktualisieren
            const transaction = exampleData.transactions.find(t => t.id === parseInt(editId));
            if (transaction) {
                Object.assign(transaction, transactionData);
                alert('Transaktion erfolgreich aktualisiert!');
            }
        } else {
            // Neue Transaktion hinzufügen
            const newId = Math.max(...exampleData.transactions.map(t => t.id), 0) + 1;
            exampleData.transactions.push({
                id: newId,
                ...transactionData
            });
            alert('Transaktion erfolgreich gespeichert!');
        }

        loadTransactions();
        closeModal();
    });

    // Suchfeld Logik & Filter
    const searchBox = document.getElementById('searchBox');
    const searchIcon = document.querySelector('.search-icon');
    if (searchBox && searchIcon) {
        searchBox.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();

            // Toggle Icon
            searchIcon.style.display = searchTerm ? 'none' : 'block';

            // Filter Table
            const rows = document.querySelectorAll('#transactionsTable tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // Select Placeholder Logik
    function updateSelectColor(select) {
        if (select.value === "") {
            select.classList.add('empty');
        } else {
            select.classList.remove('empty');
        }
    }

    selects.forEach(select => {
        updateSelectColor(select); // Initial Check
        select.addEventListener('change', () => updateSelectColor(select));
    });

    // Reset Handler für Styling
    document.getElementById('transactionForm').addEventListener('reset', () => {
        setTimeout(() => {
            selects.forEach(select => updateSelectColor(select));
        }, 0);
    });

    // IBAN Validierung und Formatierung
    const ibanInput = document.querySelector('input[name="iban"]');
    
    function formatIBAN(iban) {
        // Entferne alle Leerzeichen und konvertiere zu Großbuchstaben
        const cleaned = iban.replace(/\s/g, '').toUpperCase();
        // Füge Leerzeichen alle 4 Zeichen hinzu
        return cleaned.match(/.{1,4}/g)?.join(' ') || cleaned;
    }

    function validateIBAN(iban) {
        // Entferne Leerzeichen
        const cleaned = iban.replace(/\s/g, '');
        
        // Prüfe Länge (je nach Land unterschiedlich, hier für DE: 22)
        if (cleaned.length < 15 || cleaned.length > 34) return false;
        
        // Prüfe Format: 2 Buchstaben + 2 Ziffern + alphanumerisch
        const regex = /^[A-Z]{2}[0-9]{2}[A-Z0-9]+$/;
        if (!regex.test(cleaned)) return false;
        
        // IBAN Prüfsummenvalidierung (Modulo 97)
        const rearranged = cleaned.slice(4) + cleaned.slice(0, 4);
        const numericString = rearranged.split('').map(char => {
            const code = char.charCodeAt(0);
            return code >= 65 && code <= 90 ? code - 55 : char;
        }).join('');
        
        // Berechne Modulo 97
        let remainder = numericString.match(/.{1,9}/g).reduce((acc, part) => {
            return (parseInt(acc + part, 10) % 97).toString();
        }, '');
        
        return parseInt(remainder) === 1;
    }

    ibanInput.addEventListener('input', (e) => {
        const cursorPos = e.target.selectionStart;
        const oldValue = e.target.value;
        const oldLength = oldValue.length;
        
        // Formatiere IBAN
        e.target.value = formatIBAN(e.target.value);
        
        // Behalte Cursor-Position bei
        const newLength = e.target.value.length;
        const newCursorPos = cursorPos + (newLength - oldLength);
        e.target.setSelectionRange(newCursorPos, newCursorPos);
    });

    ibanInput.addEventListener('blur', (e) => {
        const iban = e.target.value.trim();
        if (iban && !validateIBAN(iban)) {
            e.target.setCustomValidity('Bitte geben Sie eine gültige IBAN ein.');
            e.target.reportValidity();
        } else {
            e.target.setCustomValidity('');
        }
    });

    ibanInput.addEventListener('input', () => {
        ibanInput.setCustomValidity('');
    });
});
