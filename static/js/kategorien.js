// ============ BEISPIELDATEN ============
const categoriesData = [
    {
        id: 1,
        name: 'Lebensmittel',
        typ: 'ausgabe',
        icon: '🍔',
        farbe: '#06d6a6',
        beschreibung: 'Essen und Trinken'
    },
    {
        id: 2,
        name: 'Wohnen',
        typ: 'ausgabe',
        icon: '🏠',
        farbe: '#3b82f6',
        beschreibung: 'Miete, Nebenkosten, Energie'
    },
    {
        id: 3,
        name: 'Verkehr',
        typ: 'ausgabe',
        icon: '🚗',
        farbe: '#8b5cf6',
        beschreibung: 'Auto, ÖPNV, Benzin'
    },
    {
        id: 4,
        name: 'Unterhaltung',
        typ: 'ausgabe',
        icon: '🎮',
        farbe: '#f59e0b',
        beschreibung: 'Freizeit, Hobbys, Streaming'
    },
    {
        id: 5,
        name: 'Gehalt',
        typ: 'einnahme',
        icon: '💼',
        farbe: '#ef4444',
        beschreibung: 'Monatliches Einkommen'
    },
    {
        id: 6,
        name: 'Shopping',
        typ: 'ausgabe',
        icon: '🛒',
        farbe: '#ec4899',
        beschreibung: 'Kleidung, Elektronik'
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
    document.getElementById('ausgabenCount').textContent = `${ausgaben.length} Kategorien`;
    document.getElementById('einnahmenCount').textContent = `${einnahmen.length} Kategorien`;

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
            <div class="category-item-actions">
                <button class="action-btn-round rules" onclick="openRulesModal(${category.id}, '${category.name}')" title="Regeln">
                    <span>⚙️</span>
                </button>
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
            showToast('Kategorie erfolgreich gelöscht!', 'success');
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
        beschreibung: document.querySelector('textarea[name="beschreibung"]').value || ''
    };

    if (editId) {
        const category = categoriesData.find(c => c.id === parseInt(editId));
        if (category) {
            Object.assign(category, categoryData);
            showToast('Kategorie erfolgreich aktualisiert!', 'success');
        }
    } else {
        const newId = Math.max(...categoriesData.map(c => c.id), 0) + 1;
        categoriesData.push({
            id: newId,
            ...categoryData
        });
        showToast('Kategorie erfolgreich hinzugefügt!', 'success');
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

// ============ REGELN MODAL ============

let currentRulesCategory = null;

// Beispiel-Regeln (sollten später vom Backend kommen)
const categoryRules = {
    1: ['rewe', 'edeka', 'aldi', 'lidl', 'supermarkt', 'lebensmittel'],
    2: ['miete', 'nebenkosten', 'strom', 'gas', 'wasser'],
    3: ['tankstelle', 'öpnv', 'bahn', 'bus', 'benzin', 'diesel'],
    4: ['netflix', 'spotify', 'kino', 'streaming'],
    5: ['gehalt', 'lohn'],
    6: ['amazon', 'zalando', 'ebay', 'kleidung']
};

function openRulesModal(categoryId, categoryName) {
    currentRulesCategory = categoryId;
    const category = categoriesData.find(c => c.id === categoryId);
    
    if (category) {
        document.getElementById('rulesCategoryIcon').textContent = category.icon;
        document.getElementById('rulesCategoryName').textContent = category.name;
        
        loadKeywords(categoryId);
        
        document.getElementById('rulesModal').classList.add('active');
    }
}

function closeRulesModal() {
    document.getElementById('rulesModal').classList.remove('active');
    document.getElementById('newKeywordInput').value = '';
    currentRulesCategory = null;
}

function loadKeywords(categoryId) {
    const keywords = categoryRules[categoryId] || [];
    const keywordsList = document.getElementById('keywordsList');
    
    keywordsList.innerHTML = '';
    
    if (keywords.length === 0) {
        keywordsList.innerHTML = '<div class="empty-state">Keine Schlüsselwörter definiert</div>';
    } else {
        keywords.forEach(keyword => {
            const tag = document.createElement('div');
            tag.className = 'keyword-tag';
            tag.innerHTML = `
                <span class="keyword-text">${keyword}</span>
                <button class="keyword-remove" onclick="removeKeyword('${keyword}')" title="Entfernen">×</button>
            `;
            keywordsList.appendChild(tag);
        });
    }
    
    document.getElementById('keywordsCount').textContent = keywords.length;
}

function addKeyword() {
    const input = document.getElementById('newKeywordInput');
    const keyword = input.value.trim().toLowerCase();
    
    if (!keyword) {
        showToast('Bitte geben Sie ein Schlüsselwort ein!', 'warning');
        return;
    }
    
    if (!categoryRules[currentRulesCategory]) {
        categoryRules[currentRulesCategory] = [];
    }
    
    if (categoryRules[currentRulesCategory].includes(keyword)) {
        showToast('Dieses Schlüsselwort existiert bereits!', 'warning');
        return;
    }
    
    categoryRules[currentRulesCategory].push(keyword);
    loadKeywords(currentRulesCategory);
    input.value = '';
    input.focus();
}

function removeKeyword(keyword) {
    if (confirm(`Schlüsselwort "${keyword}" wirklich entfernen?`)) {
        const index = categoryRules[currentRulesCategory].indexOf(keyword);
        if (index !== -1) {
            categoryRules[currentRulesCategory].splice(index, 1);
            loadKeywords(currentRulesCategory);
        }
    }
}

function testRules() {
    const keywords = categoryRules[currentRulesCategory] || [];
    if (keywords.length === 0) {
        showToast('Keine Regeln zum Testen vorhanden!', 'warning');
        return;
    }
    
    showToast(`Diese Kategorie wird bei folgenden Schlüsselwörtern verwendet: ${keywords.join(', ')}`, 'info', 15000);
}

// Modal Click Outside
document.getElementById('rulesModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'rulesModal') closeRulesModal();
});
