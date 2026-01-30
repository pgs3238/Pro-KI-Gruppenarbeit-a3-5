// ==================== CHATBOT JAVASCRIPT ====================
// Nutzt API_BASE_URL aus utils.js

// Elemente aus dem HTML holen
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatLoading = document.getElementById("chatLoading");

// Session-ID für diesen User
const sessionId = `user-${Math.random().toString(36).substr(2, 9)}`;

// Willkommensnachricht (zentrale Definition)
const WELCOME_MESSAGE = `Hallo! Ich bin dein Finanzassistent. Frag mich zum Beispiel:

- "Wofür gebe ich am meisten Geld aus?"
- "Wie viele Transaktionen habe ich?"
- "Zeig mir meine Bilanz für 2024"
- "Summiere alle Ausgaben für Lebensmittel"`;

// ==================== HILFSFUNKTIONEN ====================

/**
 * Fügt eine Nachricht zum Chat hinzu
 */
function addMessage(text, isUser = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user-message" : "bot-message"}`;

  // Für Bot-Nachrichten: Markdown parsen, für User: Plain-Text
  const content = isUser ? text : marked.parse(text);

  messageDiv.innerHTML = `
    <div class="message-avatar">${isUser ? "👤" : "🤖"}</div>
    <div class="message-content">
      ${content}
    </div>
  `;

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Zeigt die Willkommensnachricht an
 */
function showWelcomeMessage() {
  addMessage(WELCOME_MESSAGE, false);
}

/**
 * Zeigt den Lade-Indikator an
 */
function showLoading() {
  chatLoading.style.display = "block";
  sendButton.disabled = true;
}

/**
 * Versteckt den Lade-Indikator
 */
function hideLoading() {
  chatLoading.style.display = "none";
  sendButton.disabled = false;
}

/**
 * Sendet eine Nachricht an den Chatbot-Backend
 */
async function sendMessage(message) {
  if (!message.trim()) return;

  addMessage(message, true);
  chatInput.value = "";
  showLoading();

  try {
    const response = await fetch(`${API_BASE_URL}/chatbot/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP-Fehler: ${response.status}`);
    }

    const data = await response.json();
    addMessage(data.response, false);
  } catch (error) {
    console.error("Fehler beim Senden:", error);
    addMessage(
      "Entschuldigung, es gab einen Fehler. Bitte versuche es erneut.",
      false
    );
  } finally {
    hideLoading();
  }
}

/**
 * Zeigt ein styled Bestätigungs-Modal an
 * @param {string} message - Die anzuzeigende Nachricht
 * @param {Function} onConfirm - Callback bei Bestätigung
 */
function showConfirmModal(message, onConfirm) {
  // Erstelle Modal falls noch nicht vorhanden
  let modal = document.getElementById('confirmModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'confirmModal';
    modal.className = 'api-key-modal';
    modal.innerHTML = `
      <div class="api-modal-content" style="max-width: 400px;">
        <div class="api-modal-header">
          <h2>⚠️ Bestätigung</h2>
          <button class="api-modal-close" id="confirmModalClose">&times;</button>
        </div>
        <div class="api-modal-body">
          <p id="confirmModalMessage" style="color: #ccc; line-height: 1.6;"></p>
        </div>
        <div class="api-modal-footer">
          <button class="api-btn api-btn-cancel" id="confirmModalCancel">Abbrechen</button>
          <button class="api-btn api-btn-save" id="confirmModalOk">Bestätigen</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  // Setze Nachricht und zeige Modal
  document.getElementById('confirmModalMessage').textContent = message;
  modal.style.display = 'flex';

  // Event Handlers
  const closeModal = () => { modal.style.display = 'none'; };

  document.getElementById('confirmModalClose').onclick = closeModal;
  document.getElementById('confirmModalCancel').onclick = closeModal;
  document.getElementById('confirmModalOk').onclick = () => {
    closeModal();
    onConfirm();
  };
}

/**
 * Setzt den Chat-Verlauf zurück
 */
function resetChat() {
  showConfirmModal("Möchtest du den Chat-Verlauf wirklich löschen?", async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/chatbot/reset?session_id=${sessionId}`,
        { method: "POST" }
      );

      if (!response.ok) {
        throw new Error(`HTTP-Fehler: ${response.status}`);
      }

      // Chat leeren und Willkommensnachricht neu anzeigen
      chatMessages.innerHTML = "";
      showWelcomeMessage();

      showToast("Chat-Verlauf wurde zurückgesetzt", "success");
      console.log("Chat zurückgesetzt");
    } catch (error) {
      console.error("Fehler beim Zurücksetzen:", error);
      showToast("Fehler beim Zurücksetzen des Chats", "error");
    }
  });
}

// ==================== EVENT LISTENERS ====================

sendButton.addEventListener("click", () => {
  sendMessage(chatInput.value);
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(chatInput.value);
  }
});

chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = chatInput.scrollHeight + "px";
});

const resetButton = document.getElementById("resetChatBtn");
if (resetButton) {
  resetButton.addEventListener("click", resetChat);
}

// ==================== INITIALISIERUNG ====================

// Willkommensnachricht beim Laden anzeigen
showWelcomeMessage();

console.log("Chatbot geladen! Session-ID:", sessionId);
