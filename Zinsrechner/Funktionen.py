import math
from datetime import datetime, timedelta
from database import speichere_kontostand, hole_alle_kontostände, speichere_parameter, hole_parameter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def zeitberechnung(startdatum, zieldatum):
    start = datetime.strptime(startdatum, "%Y-%m-%d")
    ziel = datetime.strptime(zieldatum, "%Y-%m-%d")
    delta = ziel - start
    return delta.days / 365.25  # Umrechnung in Jahre

def erstelle_plot(db_name='kontostände.db', endergebnis=None, laufzeit=None):
    """
    Erstellt einen Plot mit dem Kontoverlauf aus der Datenbank
    
    Parameter:
    - db_name: Name der Datenbankdatei
    - endergebnis: Optionales Endergebnis zur Anzeige
    - laufzeit: Optionale Laufzeit in Jahren
    
    Returns:
    - plotly Figure
    """
    # Hole alle Daten aus der Datenbank
    daten = hole_alle_kontostände(db_name)
    
    if not daten:
        # Leerer Plot wenn keine Daten vorhanden
        fig = go.Figure()
        fig.add_annotation(
            text='Keine Daten verfügbar',
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(xaxis_visible=False, yaxis_visible=False)
        return fig
    
    # Extrahiere Datum und Kontostand
    daten_liste = [(datetime.strptime(row[1], "%Y-%m-%d"), row[2]) for row in daten]
    datums = [d[0] for d in daten_liste]
    kontostände = [d[1] for d in daten_liste]
    
    # Hole Parameter aus der Datenbank
    params = hole_parameter(db_name)
    
    # Erstelle Plot
    fig = go.Figure()
    
    # Hover-Text für jeden Datenpunkt
    hover_text = [
        f"Datum: {d.strftime('%Y-%m-%d')}<br>Kontostand: {k:,.2f} EUR"
        for d, k in zip(datums, kontostände)
    ]
    
    fig.add_trace(go.Scatter(
        x=datums,
        y=kontostände,
        mode='lines+markers',
        name='Kontoverlauf',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=8, color='#1f77b4', line=dict(color='white', width=2)),
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Titel mit Parametern
    if params:
        titel = f'Kontoverlauf über Zeit<br>Zinssatz: {params["zinssatz"]:.2f}% | {params["einzahlungsintervall"]}e Einzahlung: {params["einzahlung"]:.0f} EUR | Startkapital: {params["startkapital"]:.0f} EUR'
    else:
        titel = 'Kontoverlauf über Zeit'
    
    # Layout
    fig.update_layout(
        title=dict(text=titel, font=dict(size=14)),
        xaxis_title='Datum',
        yaxis_title='Kontostand (EUR)',
        hovermode='closest',
        height=600,
        showlegend=False,
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', tickformat=',.0f')
    )
    
    # Annotation für Endergebnis
    if endergebnis and laufzeit:
        fig.add_annotation(
            x=datums[-1],
            y=kontostände[-1],
            text=f'Endergebnis: {endergebnis:,.2f} EUR<br>nach {laufzeit:.1f} Jahren',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#333',
            ax=60,
            ay=-40,
            bgcolor='yellow',
            opacity=0.8,
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=11)
        )
    
    return fig
    
    # Formatiere x-Achse für Datumsanzeige
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')
    
    # Formatiere y-Achse mit Tausendertrennzeichen
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    return fig

def erstelle_vergleichs_plot(db_names):
    """
    Erstellt einen Plot mit mehreren Kontoverläufen zum Vergleich
    
    Parameter:
    - db_names: Liste von Datenbankdateinamen
    
    Returns:
    - plotly Figure
    """
    fig = go.Figure()
    
    farben = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    hat_daten = False
    
    for idx, db_name in enumerate(db_names):
        daten = hole_alle_kontostände(db_name)
        
        if daten:
            hat_daten = True
            # Extrahiere Datum und Kontostand
            daten_liste = [(datetime.strptime(row[1], "%Y-%m-%d"), row[2]) for row in daten]
            datums = [d[0] for d in daten_liste]
            kontostände = [d[1] for d in daten_liste]
            
            # Hole Parameter für Label
            params = hole_parameter(db_name)
            if params:
                label = f'Szenario {idx + 1}: {params["zinssatz"]:.1f}%, {params["einzahlungsintervall"][0]} {params["einzahlung"]:.0f}€'
            else:
                label = f'Szenario {idx + 1}'
            
            # Hover-Text
            hover_text = [
                f"<b>{label}</b><br>Datum: {d.strftime('%Y-%m-%d')}<br>Kontostand: {k:,.2f} EUR"
                for d, k in zip(datums, kontostände)
            ]
            
            # Zeichne Linie
            fig.add_trace(go.Scatter(
                x=datums,
                y=kontostände,
                mode='lines+markers',
                name=label,
                line=dict(color=farben[idx % len(farben)], width=2.5),
                marker=dict(size=7, color=farben[idx % len(farben)], 
                           line=dict(color='white', width=1.5)),
                hovertext=hover_text,
                hoverinfo='text'
            ))
    
    if not hat_daten:
        fig.add_annotation(
            text='Keine Daten verfügbar',
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(xaxis_visible=False, yaxis_visible=False)
    else:
        # Layout für Vergleichsplot
        fig.update_layout(
            title=dict(text='Vergleich der Kontoverläufe', font=dict(size=14)),
            xaxis_title='Datum',
            yaxis_title='Kontostand (EUR)',
            hovermode='closest',
            height=700,
            showlegend=True,
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)', bordercolor='#333', borderwidth=1),
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)', tickformat=',.0f')
        )
    
    return fig

def berechne_zinsen(kontostand, zinssatz, einzahlungsintervall, einzahlung, laufzeit_jahre, startdatum, kontoart, db_name='kontostände.db'):
    """
    Berechnet Zinseszins und speichert jeden Zwischenstand in der Datenbank
    
    Parameter:
    - kontostand: Startkapital
    - zinssatz: Jahreszinssatz in Prozent
    - einzahlungsintervall: Monatlich/Vierteljährlich/Jährlich
    - einzahlung: Betrag der regelmäßigen Einzahlung
    - laufzeit_jahre: Laufzeit in Jahren
    - startdatum: Startdatum als String (YYYY-MM-DD)
    - kontoart: Kontotyp für Datenbank
    - db_name: Name der Datenbankdatei
    """
    # Speichere Parameter in der Datenbank
    speichere_parameter(zinssatz, einzahlung, einzahlungsintervall, kontostand, db_name)
    
    zinssatz_dezimal = zinssatz / 100
    aktuelles_datum = datetime.strptime(startdatum, "%Y-%m-%d")
    
    for jahr in range(math.ceil(laufzeit_jahre)):
        if einzahlungsintervall == "Monatlich":
            for monat in range(12):
                kontostand += einzahlung
                kontostand *= (1 + zinssatz_dezimal / 12)
                # Datum um einen Monat erhöhen
                aktuelles_datum = aktuelles_datum + timedelta(days=30)
                # Kontostand in Datenbank speichern
                speichere_kontostand(aktuelles_datum.strftime("%Y-%m-%d"), kontostand, kontoart, db_name)
        elif einzahlungsintervall == "Vierteljährlich":
            for quartal in range(4):
                kontostand += einzahlung
                kontostand *= (1 + zinssatz_dezimal / 4)
                # Datum um ein Quartal (90 Tage) erhöhen
                aktuelles_datum = aktuelles_datum + timedelta(days=90)
                # Kontostand in Datenbank speichern
                speichere_kontostand(aktuelles_datum.strftime("%Y-%m-%d"), kontostand, kontoart, db_name)
        elif einzahlungsintervall == "Jährlich":
            kontostand += einzahlung
            kontostand *= (1 + zinssatz_dezimal)
            # Datum um ein Jahr erhöhen
            aktuelles_datum = aktuelles_datum + timedelta(days=365)
            # Kontostand in Datenbank speichern
            speichere_kontostand(aktuelles_datum.strftime("%Y-%m-%d"), kontostand, kontoart, db_name)
    
    return kontostand

