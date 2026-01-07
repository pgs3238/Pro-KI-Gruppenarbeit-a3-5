// ============ BEISPIELDATEN ============
const categoriesData = [
    {
        id: 1,
        name: 'Lebensmittel',
        typ: 'ausgabe',
        icon: '🍔',
        farbe: '#06d6a6',
        beschreibung: 'Essen und Trinken',
        anzahlTransaktionen: 45
    },
    {
        id: 2,
        name: 'Wohnen',
        typ: 'ausgabe',
        icon: '🏠',
        farbe: '#3b82f6',
        beschreibung: 'Miete, Nebenkosten, Energie',
        anzahlTransaktionen: 12
    },
    {
        id: 3,
        name: 'Verkehr',
        typ: 'ausgabe',
        icon: '🚗',
        farbe: '#8b5cf6',
        beschreibung: 'Auto, ÖPNV, Benzin',
        anzahlTransaktionen: 28
    },
    {
        id: 4,
        name: 'Unterhaltung',
        typ: 'ausgabe',
        icon: '🎮',
        farbe: '#f59e0b',
        beschreibung: 'Freizeit, Hobbys, Streaming',
        anzahlTransaktionen: 34
    },
    {
        id: 5,
        name: 'Gehalt',
        typ: 'einnahme',
        icon: '💼',
        farbe: '#ef4444',
        beschreibung: 'Monatliches Einkommen',
        anzahlTransaktionen: 3
    },
    {
        id: 6,
        name: 'Shopping',
        typ: 'ausgabe',
        icon: '🛒',
        farbe: '#ec4899',
        beschreibung: 'Kleidung, Elektronik',
        anzahlTransaktionen: 19
    }
];

// Kategorien laden und anzeigen
function loadCategories() {
    // Nach Typ gruppieren
    const ausgaben = categoriesData.filter(c => c.typ === 'ausgabe');
    const einnahmen = categoriesData.filter(c => c.typ === 'einnahme');

    // Statistiken aktualisieren
    document.getElementById('totalCategories').textContent = categoriesData.length;
    document.getElementById('ausgabenCategories').textContent = ausgaben.length;
    document.getElementById('einnahmenCategories').textContent = einnahmen.length;
    document.getElementById('ausgabenCount').textContent = ausgaben.length;
    document.getElementById('einnahmenCount').textContent = einnahmen.length;

    // Ausgaben-Liste
    const ausgabenList = document.getElementById('ausgabenList');
    ausgabenList.innerHTML = '';
    
    if (ausgaben.length === 0) {
        ausgabenList.innerHTML = '<div class="empty-state">Keine Ausgaben-Kategorien vorhanden</div>';
    } else {
        ausgaben.forEach(category => {
            ausgabenList.appendChild(createCategoryItem(category));
        });
    }

    // Einnahmen-Liste
    const einnahmenList = document.getElementById('einnahmenList');
    einnahmenList.innerHTML = '';
    
    if (einnahmen.length === 0) {
        einnahmenList.innerHTML = '<div class="empty-state">Keine Einnahmen-Kategorien vorhanden</div>';
    } else {
        einnahmen.forEach(category => {
            einnahmenList.appendChild(createCategoryItem(category));
        });
    }
}

// Kategorie-Item erstellen
function createCategoryItem(category) {
    const item = document.createElement('div');
    item.className = 'category-item';
    
    item.innerHTML = `
        <div class="category-item-left">
            <div class="category-item-icon" style="background: ${category.farbe};">
                ${category.icon}
            </div>
            <div class="category-item-info">
                <h3 class="category-item-name">${category.name}</h3>
                ${category.beschreibung ? `<p class="category-item-description">${category.beschreibung}</p>` : ''}
            </div>
        </div>
        <div class="category-item-right">
            <div class="category-item-stats">
                <span class="transaction-count">
                    <span class="count-icon">📊</span>
                    <span class="count-number">${category.anzahlTransaktionen}</span>
                </span>
            </div>
            <div class="category-item-actions">
                <button class="action-btn-round edit" onclick="editCategory(${category.id})" title="Bearbeiten">
                    <span>✏️</span>
                </button>
                <button class="action-btn-round delete" onclick="deleteCategory(${category.id})" title="Löschen">
                    <span>🗑️</span>
                </button>
            </div>
        </div>
    `;
    
    return item;
}

// Kategorie bearbeiten
function editCategory(id) {
    const category = categoriesData.find(c => c.id === id);
    if (!category) return;

    document.querySelector('input[name="name"]').value = category.name;
    document.querySelector('select[name="typ"]').value = category.typ;
    document.querySelector(`input[name="icon"][value="${category.icon}"]`).checked = true;
    document.querySelector(`input[name="farbe"][value="${category.farbe}"]`).checked = true;
    document.querySelector('textarea[name="beschreibung"]').value = category.beschreibung || '';

    document.querySelector('.modal-title').textContent = 'Kategorie bearbeiten';
    document.getElementById('categoryForm').dataset.editId = id;

    openCategoryModal();
}

// Kategorie löschen
function deleteCategory(id) {
    const category = categoriesData.find(c => c.id === id);
    if (!category) return;

    if (confirm(`Möchten Sie die Kategorie "${category.name}" wirklich löschen?`)) {
        const index = categoriesData.findIndex(c => c.id === id);
        if (index !== -1) {
            categoriesData.splice(index, 1);
            loadCategories();
            alert('Kategorie erfolgreich gelöscht!');
        }
    }
}

// Modal Funktionen
const modal = document.getElementById('categoryModal');
const selects = document.querySelectorAll('select.form-control');

function openCategoryModal() {
    modal.classList.add('active');
}

function closeCategoryModal() {
    modal.classList.remove('active');
    document.getElementById('categoryForm').reset();
    document.querySelector('.modal-title').textContent = 'Kategorie hinzufügen';
    delete document.getElementById('categoryForm').dataset.editId;
    updateSelectColors();
}

modal.addEventListener('click', (e) => {
    if (e.target === modal) closeCategoryModal();
});

// Form Submit
document.getElementById('categoryForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const form = e.target;
    const editId = form.dataset.editId;

    const categoryData = {
        name: document.querySelector('input[name="name"]').value,
        typ: document.querySelector('select[name="typ"]').value,
        icon: document.querySelector('input[name="icon"]:checked').value,
        farbe: document.querySelector('input[name="farbe"]:checked').value,
        beschreibung: document.querySelector('textarea[name="beschreibung"]').value || '',
        anzahlTransaktionen: 0
    };

    if (editId) {
        const category = categoriesData.find(c => c.id === parseInt(editId));
        if (category) {
            Object.assign(category, categoryData);
            alert('Kategorie erfolgreich aktualisiert!');
        }
    } else {
        const newId = Math.max(...categoriesData.map(c => c.id), 0) + 1;
        categoriesData.push({
            id: newId,
            ...categoryData
        });
        alert('Kategorie erfolgreich hinzugefügt!');
    }

    loadCategories();
    closeCategoryModal();
});

// Select Placeholder Styling
function updateSelectColor(select) {
    if (select.value === "") {
        select.classList.add('empty');
    } else {
        select.classList.remove('empty');
    }
}

function updateSelectColors() {
    selects.forEach(select => updateSelectColor(select));
}

selects.forEach(select => {
    updateSelectColor(select);
    select.addEventListener('change', () => updateSelectColor(select));
});

document.getElementById('categoryForm').addEventListener('reset', () => {
    setTimeout(() => updateSelectColors(), 0);
});

// Suchfunktion
const searchBox = document.getElementById('searchBox');
const searchIcon = document.querySelector('.search-icon');

if (searchBox && searchIcon) {
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        searchIcon.style.display = searchTerm ? 'none' : 'block';
        
        const cards = document.querySelectorAll('.category-card:not(.summary-card)');
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Initial laden
loadCategories();
