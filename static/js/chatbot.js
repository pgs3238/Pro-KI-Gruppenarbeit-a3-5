// ==================== CHATBOT JAVASCRIPT ====================

// API-Basis-URL (wo unser FastAPI-Backend läuft)
const API_BASE_URL = "http://localhost:8000/api";

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
    <div class="message-avatar">${isUser ? "👩‍💻" : "🤖"}</div>
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
 * Setzt den Chat-Verlauf zurück
 */
async function resetChat() {
  if (!confirm("Möchtest du den Chat-Verlauf wirklich löschen?")) {
    return;
  }

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

    console.log("Chat zurückgesetzt");
  } catch (error) {
    console.error("Fehler beim Zurücksetzen:", error);
    alert("Fehler beim Zurücksetzen des Chats.");
  }
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
