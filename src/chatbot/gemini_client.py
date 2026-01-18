"""
Gemini Chatbot mit automatischem Function Calling
"""

from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from . import tools


class GeminiChatbot:
    """
    Chatbot der Gemini API mit automatischem Function Calling nutzt,
    um auf Finanzdaten zuzugreifen
    """

    def __init__(self, api_key: str, session: Session):
        """
        Args:
            api_key: Gemini API Key
            session: SQLAlchemy Session für Datenbankzugriffe
        """
        # Gemini Client initialisieren
        self.client = genai.Client(api_key=api_key)

        # Datenbank-Session für Tools setzen
        tools.set_db_session(session)

        # Modell-Name
        self.model_name = "gemini-2.5-flash"

        # Chat-Historie
        self.chat_history = []

        # System Instruction definieren
        self.system_instruction = """
        Du bist ein intelligenter Finanz-Assistent. Deine Aufgabe ist es, Fragen zu den Finanzen des Nutzers präzise zu beantworten.
        
        WICHTIGE REGELN:
        1. NUTZE IMMER TOOLS: Rate niemals Werte. Nutze immer die bereitgestellten Funktionen, um Daten abzurufen.
        2. KEIN MANUELLES RECHNEN: Wenn der Nutzer nach Summen, Durchschnitten oder Anzahlen fragt, nutze 'get_transaction_stats' oder 'get_database_statistics'. Versuche NIEMALS, Transaktionen aus einer Liste manuell zu zählen oder zu addieren.
        3. PRÄZISION: Wenn eine Funktion 0 zurückgibt, antworte, dass es keine Ausgaben gab. Erfinde keine Daten.
        4. MEHRERE SCHRITTE: Wenn eine Frage komplexe Filter erfordert (z.B. "Lebensmittel und Miete"), rufe die entsprechenden Funktionen nacheinander auf und fasse die Ergebnisse zusammen.
        """

    def send_message(self, user_message: str) -> str:
        """
        Sendet eine Nachricht an den Chatbot mit automatischem Function Calling.

        Args:
            user_message: Benutzernachricht

        Returns:
            Antwort des Chatbots als String
        """
        try:
            # Füge Benutzernachricht zur Historie hinzu
            self.chat_history.append(
                types.Content(role="user", parts=[types.Part(text=user_message)])
            )

            # Sende Anfrage mit automatischem Function Calling
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=[
                        tools.get_transactions,
                        tools.get_spending_by_category,
                        tools.get_monthly_summary,
                        tools.get_account_overview,
                        tools.get_income_vs_expenses,
                        tools.get_categories,
                        tools.get_database_statistics,
                        tools.get_transaction_stats,
                    ],
                    # Automatisches Function Calling aktivieren
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(),
                ),
            )

            # Extrahiere Text-Antwort
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    # Sammle alle Text-Parts
                    text_parts = [
                        part.text
                        for part in candidate.content.parts
                        if hasattr(part, "text") and part.text
                    ]

                    if text_parts:
                        answer = " ".join(text_parts)

                        # Füge Antwort zur Historie hinzu
                        self.chat_history.append(candidate.content)

                        return answer

            return "Entschuldigung, ich konnte keine Antwort generieren."

        except Exception as e:
            return f"Fehler bei der Verarbeitung: {str(e)}"

    def reset_chat(self):
        """Setzt den Chat-Verlauf zurück"""
        self.chat_history = []
