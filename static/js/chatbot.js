// ==================== CHATBOT JAVASCRIPT ====================

// API-Basis-URL (wo unser FastAPI-Backend läuft)
const API_BASE_URL = "http://localhost:8000/api";

// Elemente aus dem HTML holen (mit querySelector)
const chatMessages = document.getElementById("chatMessages"); // Der Nachrichten-Container
const chatInput = document.getElementById("chatInput"); // Die Texteingabe
const sendButton = document.getElementById("sendButton"); // Der Sende-Button
const chatLoading = document.getElementById("chatLoading"); // Der Lade-Indikator

// Session-ID für diesen User (einfach: generiere zufällige ID)
const sessionId = `user-${Math.random().toString(36).substr(2, 9)}`;

// ==================== HILFSFUNKTIONEN ====================

/**
 * Fügt eine Nachricht zum Chat hinzu
 * @param {string} text - Der Nachrichtentext
 * @param {boolean} isUser - Ist es eine User-Nachricht? (true = User, false = Bot)
 */
function addMessage(text, isUser = false) {
  // Erstelle ein neues <div>-Element für die Nachricht
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user-message" : "bot-message"}`;

  // HTML-Inhalt der Nachricht (Avatar + Text)
  messageDiv.innerHTML = `
        <div class="message-avatar">${isUser ? "👩‍💻" : "🤖"}</div>
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;

  // Nachricht zum Container hinzufügen
  chatMessages.appendChild(messageDiv);

  // Scrolle automatisch nach unten (neueste Nachricht sichtbar)
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Zeigt den Lade-Indikator an
 */
function showLoading() {
  chatLoading.style.display = "block"; // Sichtbar machen
  sendButton.disabled = true; // Button deaktivieren
}

/**
 * Versteckt den Lade-Indikator
 */
function hideLoading() {
  chatLoading.style.display = "none"; // Verstecken
  sendButton.disabled = false; // Button aktivieren
}

/**
 * Sendet eine Nachricht an den Chatbot-Backend
 * @param {string} message - Die Benutzernachricht
 */
async function sendMessage(message) {
  // Leere Nachrichten ignorieren
  if (!message.trim()) return;

  // User-Nachricht zum Chat hinzufügen
  addMessage(message, true);

  // Eingabefeld leeren
  chatInput.value = "";

  // Lade-Indikator anzeigen
  showLoading();

  try {
    // HTTP POST-Request an das Backend senden
    const response = await fetch(`${API_BASE_URL}/chatbot/message`, {
      method: "POST", // POST = Daten senden
      headers: {
        "Content-Type": "application/json", // Wir senden JSON
      },
      body: JSON.stringify({
        message: message, // User-Nachricht
        session_id: sessionId, // Session-ID
      }),
    });

    // Prüfe, ob Request erfolgreich war (Status 200-299)
    if (!response.ok) {
      throw new Error(`HTTP-Fehler: ${response.status}`);
    }

    // Response als JSON parsen
    const data = await response.json();

    // Bot-Antwort zum Chat hinzufügen
    addMessage(data.response, false);
  } catch (error) {
    // Fehlerbehandlung
    console.error("Fehler beim Senden:", error);
    addMessage(
      "Entschuldigung, es gab einen Fehler. Bitte versuche es erneut.",
      false
    );
  } finally {
    // Lade-Indikator verstecken (egal ob Erfolg oder Fehler)
    hideLoading();
  }
}

// ==================== EVENT LISTENERS ====================

/**
 * Event Listener: Sende-Button geklickt
 */
sendButton.addEventListener("click", () => {
  const message = chatInput.value;
  sendMessage(message);
});

/**
 * Event Listener: Enter-Taste gedrückt (in der Textarea)
 * Shift+Enter = Neue Zeile
 * Enter allein = Senden
 */
chatInput.addEventListener("keydown", (event) => {
  // Wenn Enter (aber nicht Shift+Enter)
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault(); // Verhindere neue Zeile
    const message = chatInput.value;
    sendMessage(message);
  }
});

/**
 * Auto-Resize der Textarea (wächst mit Text)
 */
chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto"; // Reset
  chatInput.style.height = chatInput.scrollHeight + "px"; // Neue Höhe
});

// ==================== INITIALISIERUNG ====================

console.log("Chatbot geladen! Session-ID:", sessionId);
