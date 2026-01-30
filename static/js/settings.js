// ==================== API KEY MANAGEMENT ====================
// Nutzt API_BASE_URL aus utils.js

/**
 * Lädt den Status des API-Keys vom Server
 */
async function loadApiKeyStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/settings/api-key/status`);
        if (!response.ok) throw new Error('Fehler beim Laden des API-Key Status');
        
        const data = await response.json();
        
        // Zeige masked key im Input-Feld wenn vorhanden
        const apiKeyInput = document.getElementById('apiKeyInput');
        if (apiKeyInput && data.masked_key) {
            apiKeyInput.placeholder = `Aktuell: ${data.masked_key}`;
        }
        
        return data;
    } catch (error) {
        console.error('✗ Fehler beim Laden des API-Key Status:', error);
        return { configured: false };
    }
}

/**
 * Speichert den API-Key auf dem Server (in .env-Datei)
 */
async function saveApiKey(apiKey) {
    try {
        const response = await fetch(`${API_BASE_URL}/settings/api-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Speichern');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('✗ Fehler beim Speichern des API-Keys:', error);
        throw error;
    }
}

/**
 * Initialisiert den API-Key Modal Dialog
 */
function initApiKeyModal() {
    // Lade aktuellen Status beim Öffnen des Modals
    const modal = document.getElementById('apiKeyModal');
    if (!modal) return;
    
    // Event Listener für den Einstellungs-Button
    const settingsBtn = document.querySelector('.icon-btn[onclick*="apiKeyModal"]');
    if (settingsBtn) {
        // Entferne das onclick-Attribut und verwende stattdessen addEventListener
        settingsBtn.removeAttribute('onclick');
        settingsBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
            loadApiKeyStatus();
        });
    }
    
    // Event Listener für den Speichern-Button
    const saveBtn = document.querySelector('.api-btn-save');
    if (saveBtn) {
        // Entferne alte Event Listener falls vorhanden
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        
        newSaveBtn.addEventListener('click', async () => {
            const apiKeyInput = document.getElementById('apiKeyInput');
            const apiKey = apiKeyInput.value.trim();
            
            if (!apiKey) {
                showToast('Bitte geben Sie einen API-Key ein', 'error');
                return;
            }
            
            // Zeige Loading-Zustand
            newSaveBtn.disabled = true;
            newSaveBtn.textContent = 'Speichert...';
            
            try {
                const result = await saveApiKey(apiKey);
                
                if (result.success) {
                    showToast('API-Key erfolgreich gespeichert!', 'success');
                    
                    // Schließe Modal nach kurzer Verzögerung
                    setTimeout(() => {
                        modal.style.display = 'none';
                        apiKeyInput.value = '';
                    }, 1000);
                } else {
                    showToast('Fehler beim Speichern', 'error');
                }
            } catch (error) {
                showToast(error.message || 'Fehler beim Speichern', 'error');
            } finally {
                // Setze Button zurück
                newSaveBtn.disabled = false;
                newSaveBtn.textContent = 'Speichern';
            }
        });
    }
    
    // NICHT automatisch laden - nur wenn Modal geöffnet wird
}

// ==================== INITIALISIERUNG ====================

// Initialisiere API-Key Modal wenn Seite geladen ist
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApiKeyModal);
} else {
    initApiKeyModal();
}
