# Imports für Gradio UI, Datumsfunktionen und Berechnungsfunktionen
import gradio as gr
from Funktionen import zeitberechnung, berechne_zinsen, erstelle_plot, erstelle_vergleichs_plot
from database import erstelle_datenbank, loesche_alle_kontostaende
from datetime import datetime
import plotly.graph_objects as go

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
    
    # Erstelle Plot mit Endergebnis
    plot = erstelle_plot('kontostände.db', endergebnis=ergebnis, laufzeit=jahre)
    
    # Status-Nachricht
    status = f"Berechnung abgeschlossen: {ergebnis:.2f} EUR nach {jahre:.2f} Jahren"
    
    return plot, get_szenario_liste(), status

def vergleich_hinzufuegen(kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum):
    """
    Fügt eine neue Berechnung zum Vergleich hinzu (max. 5 Szenarien)
    """
    global db_list
    
    if len(db_list) >= 4:
        return erstelle_vergleichs_plot(['kontostände.db'] + db_list), get_szenario_liste(), "Maximale Anzahl (5 Szenarien) erreicht!"
    
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
    
    status = f"Szenario {len(db_list) + 1} hinzugefügt! Endergebnis: {ergebnis:.2f} EUR"
    return plot, get_szenario_liste(), status

def loesche_szenario(szenario_nr):
    """
    Löscht ein einzelnes Szenario aus dem Vergleich
    """
    global db_list
    
    if szenario_nr == 1:
        # Hauptberechnung löschen
        loesche_alle_kontostaende('kontostände.db')
        if db_list:
            plot = erstelle_vergleichs_plot(db_list)
        else:
            fig = go.Figure()
            fig.add_annotation(
                text='Keine Daten - bitte Berechnung starten',
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(xaxis_visible=False, yaxis_visible=False, height=600)
            plot = fig
        return plot, get_szenario_liste(), f"Szenario 1 gelöscht"
    elif szenario_nr > 1 and szenario_nr <= len(db_list) + 1:
        # Vergleichsszenario löschen
        db_index = szenario_nr - 2
        db_to_delete = db_list[db_index]
        loesche_alle_kontostaende(db_to_delete)
        db_list.pop(db_index)
        
        # Erstelle neuen Plot mit verbleibenden Szenarien
        if db_list:
            plot = erstelle_vergleichs_plot(['kontostände.db'] + db_list)
        else:
            plot = erstelle_plot('kontostände.db')
        
        return plot, get_szenario_liste(), f"Szenario {szenario_nr} gelöscht"
    else:
        # Aktuellen Plot beibehalten
        if db_list:
            plot = erstelle_vergleichs_plot(['kontostände.db'] + db_list)
        else:
            plot = erstelle_plot('kontostände.db')
        return plot, get_szenario_liste(), "Ungültige Szenario-Nummer"

def get_szenario_liste():
    """
    Gibt eine formatierte Liste aller aktiven Szenarien zurück
    """
    from database import hole_parameter
    
    szenarien = []
    
    # Hauptszenario
    params = hole_parameter('kontostände.db')
    if params:
        szenarien.append(f"Szenario 1: {params['zinssatz']:.2f}% | {params['einzahlungsintervall']}: {params['einzahlung']:.0f}€")
    
    # Vergleichsszenarien
    for idx, db_name in enumerate(db_list, start=2):
        params = hole_parameter(db_name)
        if params:
            szenarien.append(f"Szenario {idx}: {params['zinssatz']:.2f}% | {params['einzahlungsintervall']}: {params['einzahlung']:.0f}€")
    
    return "\n".join(szenarien) if szenarien else "Keine aktiven Szenarien"

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
    fig = go.Figure()
    fig.add_annotation(
        text='Keine Daten - bitte Berechnung starten',
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14)
    )
    fig.update_layout(xaxis_visible=False, yaxis_visible=False, height=600)
    
    # Rückgabe: kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum, plot_output, szenario_liste, status
    return 0, "", "Monatlich", 0, None, "", fig, "Keine aktiven Szenarien", "Zurückgesetzt"

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
    with gr.Row():
        with gr.Column(scale=3):
            plot_output = gr.Plot(label="Kontoverlauf")
        with gr.Column(scale=1):
            gr.Markdown("### Aktive Szenarien")
            szenario_liste = gr.Textbox(label="Szenarien", value="Keine aktiven Szenarien", lines=8, interactive=False)
            szenario_nr_input = gr.Number(label="Szenario-Nr. zum Löschen", value=1, minimum=1, maximum=5, step=1)
            loesche_btn = gr.Button("Szenario löschen", variant="secondary")
            status_output = gr.Textbox(label="Status", lines=2, interactive=False)
    
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
                     outputs=[plot_output, szenario_liste, status_output])
    
    vergleich_btn.click(fn=vergleich_hinzufuegen,
                        inputs=[kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum],
                        outputs=[plot_output, szenario_liste, status_output])
    
    loesche_btn.click(fn=loesche_szenario,
                      inputs=[szenario_nr_input],
                      outputs=[plot_output, szenario_liste, status_output])
    
    reset_btn.click(fn=reset_eingaben,
                    outputs=[kontostand, zinssatz, einzahlungsintervall, einzahlung, kontoauswahl, zieldatum, plot_output, szenario_liste, status_output])

# Starte Gradio-Webinterface
demo.launch()