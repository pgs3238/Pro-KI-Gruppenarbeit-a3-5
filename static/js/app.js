// ==================== KONFIGURATION ====================
// Nutzt API_BASE_URL aus utils.js
let availableKategorien = [];  // Cache für Kategorien
let availableKonten = [];      // Cache für Konten (global)


// ==================== KATEGORIEN LADEN ====================

/**
 * Lädt alle verfügbaren Kategorien von der API und speichert sie im Cache.
 * Aktualisiert anschließend auch alle Kategorie-Auswahlfelder.
 * @returns {Promise<Array>} Liste der Kategorien
 */
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

/**
 * Befüllt alle <select name="kategorie">-Elemente mit den geladenen Kategorien.
 * Gruppiert nach Einnahmen und Ausgaben.
 */
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


// ==================== KONTOSTAND ====================

/**
 * Lädt den Kontogesamtbetrag von der API und zeigt ihn an
 */
// Lädt alle Konten und berechnet den Gesamtsaldo. Aktualisiert die Anzeige des Gesamtsaldos im Header.
// Lädt alle Konten für den globalen Cache.
async function loadKonten() {
    try {
        // Lade die verfügbaren Konten für den Cache
        const konten = await fetchKonten();
        availableKonten = konten;  // Speichere die Konten für Lookups
        console.log('✓ Konten geladen:', konten.length);

        return konten;
    } catch (error) {
        console.error('✗ Fehler beim Laden der Konten:', error);
    }
}





// ==================== NAVIGATION ====================

/**
 * Setzt die Navigation Handler auf
 */
// Initialisiert die Click-Listener für die Navigationsleiste.
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-link');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(i => i.classList.remove('active'));
            e.currentTarget.classList.add('active');
        });
    });
}





// ==================== FAB MENU ====================

/**
 * Schaltet das FAB-Menü (Floating Action Button) ein/aus
 */
// Öffnet oder schließt das Floating Action Button (FAB) Menü.
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


// ==================== SEITEN-INITIALISIERUNG ====================

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



});
