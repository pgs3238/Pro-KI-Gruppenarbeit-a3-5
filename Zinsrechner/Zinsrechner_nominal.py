# Imports für Gradio UI, Datumsfunktionen und Berechnungsfunktionen
import gradio as gr
from Funktionen import zeitberechnung, berechne_zinsen, erstelle_plot, erstelle_vergleichs_plot
from database import erstelle_datenbank, loesche_alle_kontostaende
from datetime import datetime
import matplotlib.pyplot as plt

# Liste der verwendeten Datenbanken
db_list = []

def zinsrechner(kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum):
    """
    Hauptfunktion zur Berechnung des Zinseszinses mit regelmäßigen Einzahlungen
    und Speicherung in der Datenbank
    """
    # Lösche alte Einträge aus der Hauptdatenbank
    loesche_alle_kontostaende('kontostände.db')
    
    # Aktuelles Datum als Startdatum
    heute = datetime.now().strftime("%Y-%m-%d")
    
    # Berechne Laufzeit in Jahren
    jahre = zeitberechnung(heute, zieldatum)
    
    # Führe Zinseszinsberechnung durch
    ergebnis = berechne_zinsen(kontostand, float(zinssatz), einzahlungsintervall, einzahlung, jahre, heute, kontoauswahl, 'kontostände.db')
    
    # Erstelle Plot
    plot = erstelle_plot('kontostände.db')
    
    # Gib formatiertes Ergebnis und Plot zurück
    text_ausgabe = f"Endgültiger Kontostand nach {jahre:.2f} Jahren: {ergebnis:.2f} EUR\n(Alle Zwischenstände in Datenbank gespeichert)"
    return text_ausgabe, plot

def vergleich_hinzufuegen(kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum):
    """
    Fügt eine neue Berechnung zum Vergleich hinzu (max. 5 Szenarien)
    """
    global db_list
    
    if len(db_list) >= 4:
        return "Maximale Anzahl (5 Szenarien) erreicht!", erstelle_vergleichs_plot(['kontostände.db'] + db_list)
    
    # Erstelle neue Datenbank für Vergleich
    db_name = f'vergleich_{len(db_list) + 1}.db'
    erstelle_datenbank(db_name)
    loesche_alle_kontostaende(db_name)
    db_list.append(db_name)
    
    # Berechnung durchführen
    heute = datetime.now().strftime("%Y-%m-%d")
    jahre = zeitberechnung(heute, zieldatum)
    ergebnis = berechne_zinsen(kontostand, float(zinssatz), einzahlungsintervall, einzahlung, jahre, heute, kontoauswahl, db_name)
    
    # Erstelle Vergleichsplot mit allen Szenarien
    plot = erstelle_vergleichs_plot(['kontostände.db'] + db_list)
    
    text = f"Szenario {len(db_list) + 1} hinzugefügt! Endergebnis: {ergebnis:.2f} EUR"
    return text, plot

def reset_eingaben():
    """
    Setzt alle Eingabefelder zurück, löscht alle Datenbanken und setzt die Visualisierung zurück
    """
    global db_list
    
    # Lösche alle Einträge aus allen Datenbanken
    loesche_alle_kontostaende('kontostände.db')
    for i in range(1, 5):
        loesche_alle_kontostaende(f'vergleich_{i}.db')
    
    # Setze Vergleichsliste zurück
    db_list = []
    
    # Erstelle leeren Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.text(0.5, 0.5, 'Keine Daten - bitte Berechnung starten', 
            horizontalalignment='center', verticalalignment='center', fontsize=14)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Rückgabe: kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum, output, plot_output
    return 0, "", "Monatlich", 0, None, "", "", fig

# Initialisiere die Datenbanken beim Start
erstelle_datenbank('kontostände.db')
for i in range(1, 5):
    erstelle_datenbank(f'vergleich_{i}.db')

# Erstelle Gradio Interface mit Blocks
with gr.Blocks() as demo:
    gr.Markdown("# Zinsrechner mit Vergleichsfunktion")
    
    with gr.Row():
        with gr.Column():
            # Input-Felder
            kontostand = gr.Slider(minimum=0, maximum=100000, step=1000, label="Kontostand", value=0)
            zinssatz = gr.Textbox(label="Zinssatz %", value="")
            einzahlungsintervall = gr.Dropdown(choices=["Monatlich", "Vierteljährlich", "Jährlich"], 
                                                label="Einzahlungsintervall", value="Monatlich")
            einzahlung = gr.Slider(minimum=0, maximum=5000, step=50, label="monatliche Einzahlung", value=0)
            kontoauswahl = gr.Dropdown(choices=["Girokonto", "Tagesgeldkonto", "Depot"], label="Kontoauswahl")
            zieldatum = gr.Textbox(label="Zieldatum (YYYY-MM-DD)", value="")
            
            with gr.Row():
                submit_btn = gr.Button("Berechnen", variant="primary")
                vergleich_btn = gr.Button("Vergleich hinzufügen", variant="secondary")
                reset_btn = gr.Button("Zurücksetzen", variant="stop")
    
    # Output-Felder
    output = gr.Textbox(label="Ergebnis")
    plot_output = gr.Plot(label="Kontoverlauf")
    
    def update_label(intervall):
        """Aktualisiert das Label des Einzahlungs-Sliders"""
        if intervall == "Monatlich":
            return gr.Slider(minimum=0, maximum=5000, step=50, label="monatliche Einzahlung")
        elif intervall == "Vierteljährlich":
            return gr.Slider(minimum=0, maximum=5000, step=50, label="vierteljährliche Einzahlung")
        else:  # Jährlich
            return gr.Slider(minimum=0, maximum=5000, step=50, label="jährliche Einzahlung")
    
    # Event-Handler
    einzahlungsintervall.change(fn=update_label, inputs=einzahlungsintervall, outputs=einzahlung)
    
    submit_btn.click(fn=zinsrechner, 
                     inputs=[kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum], 
                     outputs=[output, plot_output])
    
    vergleich_btn.click(fn=vergleich_hinzufuegen,
                        inputs=[kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum],
                        outputs=[output, plot_output])
    
    reset_btn.click(fn=reset_eingaben,
                    outputs=[kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum, output, plot_output])

# Starte Gradio-Webinterface
demo.launch()