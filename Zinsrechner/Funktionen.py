import math
from datetime import datetime, timedelta
from database import speichere_kontostand, hole_alle_kontostände
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def zeitberechnung(startdatum, zieldatum):
    start = datetime.strptime(startdatum, "%Y-%m-%d")
    ziel = datetime.strptime(zieldatum, "%Y-%m-%d")
    delta = ziel - start
    return delta.days / 365.25  # Umrechnung in Jahre

def erstelle_plot(db_name='kontostände.db'):
    """
    Erstellt einen Plot mit dem Kontoverlauf aus der Datenbank
    
    Parameter:
    - db_name: Name der Datenbankdatei
    
    Returns:
    - matplotlib Figure
    """
    # Hole alle Daten aus der Datenbank
    daten = hole_alle_kontostände(db_name)
    
    if not daten:
        # Leerer Plot wenn keine Daten vorhanden
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Keine Daten verfügbar', 
                horizontalalignment='center', verticalalignment='center')
        return fig
    
    # Extrahiere Datum und Kontostand
    daten_liste = [(datetime.strptime(row[1], "%Y-%m-%d"), row[2]) for row in daten]
    datums = [d[0] for d in daten_liste]
    kontostände = [d[1] for d in daten_liste]
    
    # Erstelle Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(datums, kontostände, marker='o', linestyle='-', linewidth=2, markersize=4)
    
    # Formatierung
    ax.set_xlabel('Datum', fontsize=12)
    ax.set_ylabel('Kontostand (EUR)', fontsize=12)
    ax.set_title('Kontoverlauf über Zeit', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
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
    - matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    farben = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    min_y, max_y = float('inf'), float('-inf')
    
    for idx, db_name in enumerate(db_names):
        daten = hole_alle_kontostände(db_name)
        
        if daten:
            # Extrahiere Datum und Kontostand
            daten_liste = [(datetime.strptime(row[1], "%Y-%m-%d"), row[2]) for row in daten]
            datums = [d[0] for d in daten_liste]
            kontostände = [d[1] for d in daten_liste]
            
            # Aktualisiere y-Achsen-Grenzen
            min_y = min(min_y, min(kontostände))
            max_y = max(max_y, max(kontostände))
            
            # Zeichne Linie
            ax.plot(datums, kontostände, marker='o', linestyle='-', 
                   linewidth=2, markersize=3, color=farben[idx % len(farben)],
                   label=f'Szenario {idx + 1}')
    
    if min_y == float('inf'):
        ax.text(0.5, 0.5, 'Keine Daten verfügbar', 
                horizontalalignment='center', verticalalignment='center')
    else:
        # Setze gleiche Skalierung für alle Plots
        y_padding = (max_y - min_y) * 0.1
        ax.set_ylim(min_y - y_padding, max_y + y_padding)
    
    # Formatierung
    ax.set_xlabel('Datum', fontsize=12)
    ax.set_ylabel('Kontostand (EUR)', fontsize=12)
    ax.set_title('Vergleich der Kontoverläufe', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    # Formatiere x-Achse für Datumsanzeige
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')
    
    # Formatiere y-Achse mit Tausendertrennzeichen
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
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

