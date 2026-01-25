// ============ API KONFIGURATION ============
// Verwende die API auf localhost:8000, unabhängig davon, wo die HTML serviert wird
const API_BASE_URL = 'http://localhost:8000/api/categories';

// ============ KATEGORIEN VON BACKEND LADEN ============
let categoriesData = [];

// Kategorien laden und anzeigen
async function loadCategories() {
    try {
        // Kategorien vom Backend laden
        const response = await fetch(API_BASE_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const categories = await response.json();
        categoriesData = categories;
        renderCategories(categories);
    } catch (error) {
        console.error('Fehler beim Laden der Kategorien:', error);
        showToast('Fehler beim Laden der Kategorien', 'error');
    }
}

// Kategorien rendern
function renderCategories(categories) {
    console.log('Alle Kategorien erhalten vom Backend:', categories);
    
    // Nach Typ gruppieren (Ausgabe vs. Einnahme)
    const ausgaben = categories.filter(c => c.category_type === 'Ausgabe');
    const einnahmen = categories.filter(c => c.category_type === 'Einnahme');

    console.log('Ausgaben gefiltert:', ausgaben);
    console.log('Einnahmen gefiltert:', einnahmen);

    // Statistiken aktualisieren
    document.getElementById('totalCategories').textContent = categories.length;
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
    
    // Verwende standardmäßige Icons basierend auf dem Namen
    const iconMap = {
        'Lebensmittel': '🍔',
        'Wohnen': '🏠',
        'Miete': '🏠',
        'Verkehr': '🚗',
        'Transport': '🚗',
        'Unterhaltung': '🎮',
        'Freizeit': '🎮',
        'Gehalt': '💼',
        'Shopping': '🛒',
        'Versicherung': '🛡️',
        'Strom & Gas': '⚡',
        'Internet & Telefon': '📱',
        'Abos & Mitgliedschaften': '📺',
        'Rücklagen': '🏦'
    };

    // Farben basierend auf Kategorie-Typ
    const colorMap = {
        'Ausgabe': '#ef4444',
        'Einnahme': '#06d6a6'
    };

    // Verwende das gespeicherte Icon, falls vorhanden, ansonsten Fallback auf iconMap oder default
    const icon = category.icon || iconMap[category.name] || '🏷️';
    // Verwende die gespeicherte Farbe, falls vorhanden, ansonsten Fallback auf colorMap oder default
    const color = category.farbe || colorMap[category.category_type] || '#06d6a6';
    
    item.innerHTML = `
        <div class="category-item-left">
            <div class="category-item-icon" style="background: ${color};">
                ${icon}
            </div>
            <div class="category-item-info">
                <h3 class="category-item-name">${category.name}</h3>
                <p class="category-item-description">${category.category_type}</p>
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
    document.querySelector('select[name="typ"]').value = category.category_type;
    
    // Setze das gespeicherte Icon, falls vorhanden, ansonsten das erste Icon als Default
    const iconToCheck = document.querySelector(`input[name="icon"][value="${category.icon}"]`);
    if (iconToCheck) {
        iconToCheck.checked = true;
    } else {
        document.querySelector('input[name="icon"][value="🍔"]').checked = true;
    }
    
    // Setze die gespeicherte Farbe, falls vorhanden, ansonsten die Default-Farbe
    const colorToCheck = document.querySelector(`input[name="farbe"][value="${category.farbe}"]`);
    if (colorToCheck) {
        colorToCheck.checked = true;
    } else {
        document.querySelector('input[name="farbe"][value="#06d6a6"]').checked = true;
    }
    
    document.querySelector('textarea[name="beschreibung"]').value = '';

    document.querySelector('.modal-title').textContent = 'Kategorie bearbeiten';
    document.getElementById('categoryForm').dataset.editId = id;

    openCategoryModal();
}

// Kategorie löschen
async function deleteCategory(id) {
    const category = categoriesData.find(c => c.id === id);
    if (!category) return;

    if (confirm(`Möchten Sie die Kategorie "${category.name}" wirklich löschen?`)) {
        try {
            const response = await fetch(`http://localhost:8000/api/categories/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Fehler beim Löschen');
            }

            categoriesData = categoriesData.filter(c => c.id !== id);
            loadCategories();
            showToast('Kategorie erfolgreich gelöscht!', 'success');
        } catch (error) {
            console.error('Fehler beim Löschen der Kategorie:', error);
            showToast(error.message || 'Fehler beim Löschen der Kategorie', 'error');
        }
    }
}

// Modal Funktionen
const modal = document.getElementById('categoryModal');
const selects = document.querySelectorAll('select.form-control');

function openCategoryModal() {
    // Stelle sicher, dass ein Typ ausgewählt ist (Standard: Ausgabe)
    const typSelect = document.querySelector('select[name="typ"]');
    if (typSelect && !typSelect.value) {
        typSelect.value = 'Ausgabe';
    }
    
    // Stelle sicher, dass ein Icon ausgewählt ist (Standard: erstes Icon)
    const iconInputs = document.querySelectorAll('input[name="icon"]');
    if (iconInputs.length > 0 && !document.querySelector('input[name="icon"]:checked')) {
        iconInputs[0].checked = true;
    }
    
    // Stelle sicher, dass eine Farbe ausgewählt ist (Standard: erste Farbe)
    const farbeInputs = document.querySelectorAll('input[name="farbe"]');
    if (farbeInputs.length > 0 && !document.querySelector('input[name="farbe"]:checked')) {
        farbeInputs[0].checked = true;
    }
    
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
document.getElementById('categoryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const editId = form.dataset.editId;

    const iconElement = document.querySelector('input[name="icon"]:checked');
    const farbeElement = document.querySelector('input[name="farbe"]:checked');
    
    console.log('Ausgewähltes Icon:', iconElement ? iconElement.value : 'KEINE AUSWAHL');
    console.log('Ausgewählte Farbe:', farbeElement ? farbeElement.value : 'KEINE AUSWAHL');

    const categoryData = {
        name: document.querySelector('input[name="name"]').value,
        category_type: document.querySelector('select[name="typ"]').value,
        icon: iconElement ? iconElement.value : '🏷️',
        farbe: farbeElement ? farbeElement.value : '#06d6a6'
    };

    console.log('CategoryData:', categoryData);

    try {
        let response;
        if (editId) {
            // Update existierende Kategorie
            response = await fetch(`http://localhost:8000/api/categories/${editId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });
        } else {
            // Erstelle neue Kategorie
            response = await fetch('http://localhost:8000/api/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Speichern');
        }

        const savedCategory = await response.json();

        if (editId) {
            showToast('Kategorie erfolgreich aktualisiert!', 'success');
        } else {
            showToast('Kategorie erfolgreich hinzugefügt!', 'success');
        }

        loadCategories();
        closeCategoryModal();
    } catch (error) {
        console.error('Fehler beim Speichern der Kategorie:', error);
        showToast(error.message || 'Fehler beim Speichern der Kategorie', 'error');
    }
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
let currentRulesCategoryId = null;

function openRulesModal(categoryId, categoryName) {
    currentRulesCategory = categoryName;
    currentRulesCategoryId = categoryId;
    const category = categoriesData.find(c => c.id === categoryId);
    
    if (category) {
        // Icon basierend auf Kategorienamen
        const iconMap = {
            'Lebensmittel': '🍔',
            'Wohnen': '🏠',
            'Miete': '🏠',
            'Verkehr': '🚗',
            'Transport': '🚗',
            'Unterhaltung': '🎮',
            'Freizeit': '🎮',
            'Gehalt': '💼',
            'Shopping': '🛒',
            'Versicherung': '🛡️',
            'Strom & Gas': '⚡',
            'Internet & Telefon': '📱',
            'Abos & Mitgliedschaften': '📺',
            'Rücklagen': '🏦'
        };
        
        const icon = iconMap[category.name] || '🏷️';
        document.getElementById('rulesCategoryIcon').textContent = icon;
        document.getElementById('rulesCategoryName').textContent = category.name;
        
        loadKeywords(categoryId);
        
        document.getElementById('rulesModal').classList.add('active');
    }
}

function closeRulesModal() {
    document.getElementById('rulesModal').classList.remove('active');
    document.getElementById('newKeywordInput').value = '';
    currentRulesCategory = null;
    currentRulesCategoryId = null;
}

async function loadKeywords(categoryId) {
    try {
        const response = await fetch(`http://localhost:8000/api/categories/${categoryId}/rules`);
        if (!response.ok) {
            throw new Error('Fehler beim Laden der Regeln');
        }

        const rulesData = await response.json();
        const keywords = rulesData.keywords || [];
        
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
    } catch (error) {
        console.error('Fehler beim Laden der Schlüsselwörter:', error);
        showToast('Fehler beim Laden der Schlüsselwörter', 'error');
    }
}

async function addKeyword() {
    const input = document.getElementById('newKeywordInput');
    const keyword = input.value.trim().toLowerCase();
    
    if (!keyword) {
        showToast('Bitte geben Sie ein Schlüsselwort ein!', 'warning');
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/api/categories/${currentRulesCategoryId}/rules/keywords`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keyword: keyword })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Hinzufügen');
        }

        showToast('Schlüsselwort erfolgreich hinzugefügt!', 'success');
        await loadKeywords(currentRulesCategoryId);
        input.value = '';
        input.focus();
    } catch (error) {
        console.error('Fehler beim Hinzufügen des Schlüsselworts:', error);
        showToast(error.message || 'Fehler beim Hinzufügen des Schlüsselworts', 'error');
    }
}

async function removeKeyword(keyword) {
    if (confirm(`Schlüsselwort "${keyword}" wirklich entfernen?`)) {
        try {
            const encodedKeyword = encodeURIComponent(keyword);
            const response = await fetch(`http://localhost:8000/api/categories/${currentRulesCategoryId}/rules/keywords/${encodedKeyword}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Fehler beim Löschen');
            }

            showToast('Schlüsselwort erfolgreich gelöscht!', 'success');
            await loadKeywords(currentRulesCategoryId);
        } catch (error) {
            console.error('Fehler beim Löschen des Schlüsselworts:', error);
            showToast(error.message || 'Fehler beim Löschen des Schlüsselworts', 'error');
        }
    }
}

function testRules() {
    // Diese Funktion wird nicht mehr benötigt, da wir die echten Daten haben
    showToast('Regeln werden automatisch beim Kategorisieren verwendet.', 'info', 5000);
}

// Modal Click Outside
document.getElementById('rulesModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'rulesModal') closeRulesModal();
});
