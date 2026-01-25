// ============ ZINSRECHNER JAVASCRIPT MIT CUSTOM LEGEND ============

const API_BASE = 'http://localhost:8000/api';
let chart = null;
let berechnungen = [];
let ausgewaehlteId = null;
let vorschauAktiv = false;
let vorschauTimeout = null;
let kontenListe = [];

// ============ CUSTOM LEGEND PLUGIN ============
const getOrCreateLegendList = (chart, id) => {
    const legendContainer = document.getElementById(id);
    let listContainer = legendContainer.querySelector('ul');
    
    if (!listContainer) {
        listContainer = document.createElement('ul');
        listContainer.style.cssText = 'margin: 0; padding: 0; list-style: none; display: flex; flex-direction: row; flex-wrap: wrap; gap: 6px;';
        legendContainer.appendChild(listContainer);
    }
    
    return listContainer;
};

const htmlLegendPlugin = {
    id: 'htmlLegend',
    afterUpdate(chart, args, options) {
        const ul = getOrCreateLegendList(chart, options.containerID);
        
        // Alte Items entfernen
        while (ul.firstChild) {
            ul.firstChild.remove();
        }
        
        // Neue Items erstellen (nur echte Berechnungen, keine Vorschau)
        chart.data.datasets.forEach((dataset, i) => {
            // Vorschau überspringen
            if (dataset.label && dataset.label === 'Vorschau') return;
            
            const li = document.createElement('li');
            li.style.cssText = 'display: flex; align-items: center; gap: 6px; padding: 4px 8px; background: #2a2a2a; border-radius: 6px;';
            
            // Farbpunkt
            const colorBox = document.createElement('span');
            colorBox.style.cssText = `background: ${dataset.borderColor}; width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;`;
            
            // Label mit Click-Handler zum Auswählen
            const textContainer = document.createElement('span');
            textContainer.style.cssText = 'color: #ccc; font-size: 11px; flex: 1; cursor: pointer; white-space: nowrap;';
            textContainer.textContent = dataset.label;
            textContainer.onclick = () => {
                // Berechnung auswählen basierend auf Dataset-Index
                const berIndex = parseInt(dataset.berechnungIndex);
                if (!isNaN(berIndex) && berIndex >= 0 && berIndex < berechnungen.length) {
                    waehleBerechnung(berechnungen[berIndex].id);
                }
            };
            
            // Sichtbarkeits-Button (Auge)
            const visibilityBtn = document.createElement('button');
            const istSichtbar = chart.isDatasetVisible(i);
            visibilityBtn.innerHTML = istSichtbar ? '👁️' : '👁️‍🗨️';
            visibilityBtn.style.cssText = 'background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px; opacity: 0.7; transition: opacity 0.2s;';
            visibilityBtn.title = istSichtbar ? 'Ausblenden' : 'Einblenden';
            visibilityBtn.onmouseover = () => visibilityBtn.style.opacity = '1';
            visibilityBtn.onmouseout = () => visibilityBtn.style.opacity = '0.7';
            visibilityBtn.onclick = () => {
                chart.setDatasetVisibility(i, !chart.isDatasetVisible(i));
                chart.update('none');
            };
            
            // Löschen-Button (X)
            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '✕';
            deleteBtn.style.cssText = 'background: #d63447; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 12px; padding: 2px 6px; font-weight: bold; transition: all 0.2s;';
            deleteBtn.title = 'Berechnung löschen';
            deleteBtn.onmouseover = () => {
                deleteBtn.style.background = '#ff5566';
                deleteBtn.style.transform = 'scale(1.1)';
            };
            deleteBtn.onmouseout = () => {
                deleteBtn.style.background = '#d63447';
                deleteBtn.style.transform = 'scale(1)';
            };
            deleteBtn.onclick = () => {
                const berIndex = parseInt(dataset.berechnungIndex);
                if (!isNaN(berIndex) && berIndex >= 0 && berIndex < berechnungen.length) {
                    loescheBerechnungById(berechnungen[berIndex].id);
                }
            };
            
            li.appendChild(colorBox);
            li.appendChild(textContainer);
            li.appendChild(visibilityBtn);
            li.appendChild(deleteBtn);
            ul.appendChild(li);
        });
    }
};

// ============ INITIALISIERUNG ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('Zinsrechner wird initialisiert...');
    
    // Logo initial anzeigen
    document.getElementById('placeholderLogo').style.display = 'flex';
    document.getElementById('chartBereich').style.display = 'none';
    
    initChart();
    setupEventListeners();
    updateSliderLabels();
    ladeAlleVergleiche();
    ladeKonten();
    console.log('Zinsrechner erfolgreich geladen!');
});

// ============ CHART INITIALISIERUNG ============
function initChart() {
    const ctx = document.getElementById('zinsChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false  // Native Legend ausblenden
                },
                htmlLegend: {
                    containerID: 'legendContainer'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a1a1a',
                    titleColor: '#06d6a6',
                    bodyColor: '#ccc',
                    borderColor: '#06d6a6',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += formatCurrency(context.parsed.y);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#888',
                        callback: function(value) {
                            return Math.round(value).toLocaleString('de-DE') + ' €';
                        }
                    },
                    grid: { color: '#333' }
                },
                x: {
                    ticks: { color: '#888' },
                    grid: { color: '#333' }
                }
            }
        },
        plugins: [htmlLegendPlugin, {
            id: 'watermark',
            afterDraw: (chart) => {
                if (chart.data.datasets.length === 0 || chart.data.datasets.every(ds => ds.hidden)) {
                    const ctx = chart.ctx;
                    const width = chart.width;
                    const height = chart.height;
                    
                    ctx.save();
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = 'bold 48px Arial';
                    ctx.fillStyle = 'rgba(6, 214, 166, 0.1)';
                    ctx.fillText('FINLY', width / 2, height / 2);
                    ctx.restore();
                }
            }
        }]
    });
}

// ============ EVENT LISTENERS ============
function setupEventListeners() {
    document.getElementById('kontostand').addEventListener('input', () => {
        updateSliderLabels();
        triggereVorschau();
    });
    document.getElementById('einzahlung').addEventListener('input', () => {
        updateSliderLabels();
        triggereVorschau();
    });
    document.getElementById('laufzeit').addEventListener('input', () => {
        updateSliderLabels();
        triggereVorschau();
    });
    document.getElementById('zinssatz').addEventListener('input', () => {
        updateSliderLabels();
        triggereVorschau();
    });
    
    document.getElementById('intervall').addEventListener('change', () => {
        const intervall = document.getElementById('intervall').value;
        const label = document.querySelector('label[for="einzahlung"]');
        if (intervall === 'Monatlich') label.textContent = 'Monatliche Einzahlung';
        else if (intervall === 'Vierteljährlich') label.textContent = 'Vierteljährliche Einzahlung';
        else label.textContent = 'Jährliche Einzahlung';
        triggereVorschau();
    });
    
    document.querySelectorAll('input[name="kontostandTyp"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const istFiktiv = e.target.value === 'fiktiv';
            document.getElementById('kontostandEingabe').style.display = istFiktiv ? 'block' : 'none';
            document.getElementById('kontenauswahlGruppe').style.display = istFiktiv ? 'none' : 'block';
            
            const label = document.querySelector('label[for="kontostand"]');
            label.textContent = istFiktiv ? 'Startkapital (Fiktiv)' : 'Startkapital (Aktuell)';
            
            triggereVorschau();
        });
    });
    
    document.getElementById('kontoauswahl').addEventListener('change', (e) => {
        const selectedIban = e.target.value;
        if (selectedIban) {
            const konto = kontenListe.find(k => k.iban === selectedIban);
            if (konto) {
                document.getElementById('kontostand').value = Math.max(0, Math.round(konto.kontostand));
                updateSliderLabels();
                
                document.getElementById('kontoInfo').textContent = 
                    `Aktueller Kontostand: ${formatCurrency(konto.kontostand)} (${konto.anzahl_transaktionen} Transaktionen)`;
                
                triggereVorschau();
            }
        }
    });
    
    document.getElementById('berechnenBtn').addEventListener('click', berechnen);
    document.getElementById('aktualisierenBtn').addEventListener('click', aktualisieren);
    document.getElementById('resetBtn').addEventListener('click', zuruecksetzen);
}

// ============ SLIDER LABELS AKTUALISIEREN ============
function updateSliderLabels() {
    const zinssatz = document.getElementById('zinssatz').value;
    const kontostand = document.getElementById('kontostand').value;
    const einzahlung = document.getElementById('einzahlung').value;
    const laufzeit = document.getElementById('laufzeit').value;
    
    document.getElementById('zinssatzWert').textContent = zinssatz + '%';
    document.getElementById('kontostandWert').textContent = formatCurrency(kontostand);
    document.getElementById('einzahlungWert').textContent = formatCurrency(einzahlung);
    document.getElementById('laufzeitWert').textContent = laufzeit + ' Jahre';
}

// ============ VORSCHAU-FUNKTION ============
function triggereVorschau() {
    if (!ausgewaehlteId) return;
    
    vorschauAktiv = true;
    
    if (vorschauTimeout) clearTimeout(vorschauTimeout);
    vorschauTimeout = setTimeout(() => {
        aktualisiereChartMitVorschau();
    }, 300);
}

async function aktualisiereChartMitVorschau() {
    const kontostandTyp = document.querySelector('input[name="kontostandTyp"]:checked').value;
    let startkapital;
    
    if (kontostandTyp === 'aktuell') {
        try {
            const response = await fetch(`${API_BASE}/kontostand`);
            const data = await response.json();
            if (data.success) {
                startkapital = data.kontostand;
            } else {
                return;
            }
        } catch (error) {
            return;
        }
    } else {
        startkapital = parseFloat(document.getElementById('kontostand').value);
    }
    
    const zinssatz = parseFloat(document.getElementById('zinssatz').value);
    const intervall = document.getElementById('intervall').value;
    const einzahlung = parseFloat(document.getElementById('einzahlung').value);
    const laufzeit = parseFloat(document.getElementById('laufzeit').value);
    
    const ergebnis = berechneZinseszins(startkapital, zinssatz, intervall, einzahlung, laufzeit);
    aktualisiereChart(ergebnis.verlauf);
}

// ============ HAUPTFUNKTION: BERECHNEN ============
async function berechnen() {
    const kontostandTyp = document.querySelector('input[name="kontostandTyp"]:checked').value;
    let startkapital;
    
    if (kontostandTyp === 'aktuell') {
        try {
            const response = await fetch(`${API_BASE}/kontostand`);
            const data = await response.json();
            if (data.success) {
                startkapital = data.kontostand;
            } else {
                alert('Fehler beim Laden des Kontostands!');
                return;
            }
        } catch (error) {
            alert('Server nicht erreichbar!');
            return;
        }
    } else {
        startkapital = parseFloat(document.getElementById('kontostand').value);
    }
    
    const zinssatz = parseFloat(document.getElementById('zinssatz').value);
    const intervall = document.getElementById('intervall').value;
    const einzahlung = parseFloat(document.getElementById('einzahlung').value);
    const laufzeit = parseFloat(document.getElementById('laufzeit').value);
    
    const ergebnis = berechneZinseszins(startkapital, zinssatz, intervall, einzahlung, laufzeit);
    
    const neueBerechnung = {
        id: Date.now(),
        verlauf: ergebnis.verlauf,
        parameter: {
            startkapital: startkapital,
            zinssatz: zinssatz,
            intervall: intervall,
            einzahlung: einzahlung,
            laufzeit: laufzeit,
            kontostandTyp: kontostandTyp
        }
    };
    
    if (berechnungen.length >= 3) {
        alert('Maximale Anzahl von 3 Berechnungen erreicht. Bitte löschen Sie zuerst eine Berechnung.');
        return;
    }
    
    const dbNummer = berechnungen.length + 1;
    const saveResult = await speichereVergleich(dbNummer, neueBerechnung.verlauf, neueBerechnung.parameter);
    
    if (!saveResult.success) {
        alert('Fehler beim Speichern der Berechnung!');
        return;
    }
    
    berechnungen.push(neueBerechnung);
    ausgewaehlteId = neueBerechnung.id;
    
    zeigeErgebnis(neueBerechnung);
    aktualisiereListe();
    vorschauAktiv = false;
    aktualisiereChart();
    
    document.getElementById('aktualisierenBtn').style.display = 'block';
    document.getElementById('berechnenBtn').textContent = 'Berechnen (Neu)';
}

// ============ HAUPTFUNKTION: AKTUALISIEREN ============
async function aktualisieren() {
    if (!ausgewaehlteId) {
        alert('Bitte wählen Sie zuerst eine Berechnung aus!');
        return;
    }
    
    const kontostandTyp = document.querySelector('input[name="kontostandTyp"]:checked').value;
    let startkapital;
    
    if (kontostandTyp === 'aktuell') {
        try {
            const response = await fetch(`${API_BASE}/kontostand`);
            const data = await response.json();
            if (data.success) {
                startkapital = data.kontostand;
            } else {
                alert('Fehler beim Laden des Kontostands!');
                return;
            }
        } catch (error) {
            alert('Server nicht erreichbar!');
            return;
        }
    } else {
        startkapital = parseFloat(document.getElementById('kontostand').value);
    }
    
    const zinssatz = parseFloat(document.getElementById('zinssatz').value);
    const intervall = document.getElementById('intervall').value;
    const einzahlung = parseFloat(document.getElementById('einzahlung').value);
    const laufzeit = parseFloat(document.getElementById('laufzeit').value);
    
    const ergebnis = berechneZinseszins(startkapital, zinssatz, intervall, einzahlung, laufzeit);
    
    const index = berechnungen.findIndex(b => b.id === ausgewaehlteId);
    if (index !== -1) {
        berechnungen[index].verlauf = ergebnis.verlauf;
        berechnungen[index].parameter = {
            startkapital: startkapital,
            zinssatz: zinssatz,
            intervall: intervall,
            einzahlung: einzahlung,
            laufzeit: laufzeit,
            kontostandTyp: kontostandTyp
        };
        
        const dbNummer = index + 1;
        await speichereVergleich(dbNummer, berechnungen[index].verlauf, berechnungen[index].parameter);
        
        zeigeErgebnis(berechnungen[index]);
        aktualisiereListe();
        vorschauAktiv = false;
        aktualisiereChart();
    }
}

// ============ ZINSESZINS-BERECHNUNG ============
function berechneZinseszins(startkapital, zinssatz, intervall, einzahlung, laufzeitJahre) {
    const zins = zinssatz / 100;
    let periodenProJahr;
    
    if (intervall === 'Monatlich') periodenProJahr = 12;
    else if (intervall === 'Vierteljährlich') periodenProJahr = 4;
    else periodenProJahr = 1;
    
    const gesamtPerioden = laufzeitJahre * periodenProJahr;
    const periodZins = zins / periodenProJahr;
    
    let verlauf = [];
    let kapital = startkapital;
    
    verlauf.push({
        jahr: new Date().getFullYear(),
        periode: 0,
        kapital: kapital,
        einzahlungGesamt: 0,
        zinsenGesamt: 0
    });
    
    let gesamtEinzahlung = 0;
    let gesamtZinsen = 0;
    
    for (let periode = 1; periode <= gesamtPerioden; periode++) {
        const zinsen = kapital * periodZins;
        kapital += zinsen + einzahlung;
        gesamtEinzahlung += einzahlung;
        gesamtZinsen += zinsen;
        
        if (periode % periodenProJahr === 0) {
            verlauf.push({
                jahr: new Date().getFullYear() + Math.floor(periode / periodenProJahr),
                periode: periode,
                kapital: kapital,
                einzahlungGesamt: gesamtEinzahlung,
                zinsenGesamt: gesamtZinsen
            });
        }
    }
    
    return {
        verlauf: verlauf,
        endkapital: kapital,
        gesamtEinzahlung: gesamtEinzahlung,
        gesamtZinsen: gesamtZinsen
    };
}

// ============ UI UPDATES ============
function zeigeErgebnis(berechnung) {
    const letzter = berechnung.verlauf[berechnung.verlauf.length - 1];
    const jahre = berechnung.parameter.laufzeit;
    
    document.getElementById('ergebnisJahre').textContent = jahre;
    document.getElementById('endergebnis').textContent = formatCurrency(letzter.kapital);
    document.getElementById('einzahlungGesamt').textContent = formatCurrency(letzter.einzahlungGesamt);
    document.getElementById('zinsenGesamt').textContent = formatCurrency(letzter.zinsenGesamt);
    document.getElementById('ergebnisBox').style.display = 'block';
}

function aktualisiereListe() {
    const anzahl = berechnungen.length;
    document.getElementById('berechnungenAnzahl').textContent = anzahl;
    
    // Toggle zwischen Logo und Chart
    const placeholderLogo = document.getElementById('placeholderLogo');
    const chartBereich = document.getElementById('chartBereich');
    
    if (anzahl === 0) {
        placeholderLogo.style.display = 'flex';
        chartBereich.style.display = 'none';
    } else {
        placeholderLogo.style.display = 'none';
        chartBereich.style.display = 'flex';
    }
}

function waehleBerechnung(id) {
    ausgewaehlteId = id;
    const berechnung = berechnungen.find(b => b.id === id);
    if (berechnung) {
        zeigeErgebnis(berechnung);
        ladeParameterInsFormular(berechnung);
        aktualisiereListe();
        aktualisiereChart();
        
        document.getElementById('aktualisierenBtn').style.display = 'block';
        document.getElementById('berechnenBtn').textContent = 'Berechnen (Neu)';
    }
}

function ladeParameterInsFormular(berechnung) {
    const p = berechnung.parameter;
    
    vorschauAktiv = false;
    
    document.querySelector(`input[name="kontostandTyp"][value="${p.kontostandTyp}"]`).checked = true;
    
    const istFiktiv = p.kontostandTyp === 'fiktiv';
    document.getElementById('kontostandEingabe').style.display = istFiktiv ? 'block' : 'none';
    document.getElementById('kontenauswahlGruppe').style.display = istFiktiv ? 'none' : 'block';
    
    const label = document.querySelector('label[for="kontostand"]');
    label.textContent = istFiktiv ? 'Startkapital (Fiktiv)' : 'Startkapital (Aktuell)';
    
    document.getElementById('zinssatz').value = p.zinssatz;
    document.getElementById('kontostand').value = p.startkapital;
    document.getElementById('einzahlung').value = p.einzahlung;
    document.getElementById('laufzeit').value = p.laufzeit;
    document.getElementById('intervall').value = p.intervall;
    
    const einzahlungLabel = document.querySelector('label[for="einzahlung"]');
    if (p.intervall === 'Monatlich') einzahlungLabel.textContent = 'Monatliche Einzahlung';
    else if (p.intervall === 'Vierteljährlich') einzahlungLabel.textContent = 'Vierteljährliche Einzahlung';
    else einzahlungLabel.textContent = 'Jährliche Einzahlung';
    
    updateSliderLabels();
    
    setTimeout(() => {
        vorschauAktiv = true;
    }, 100);
}

function aktualisiereChart(vorschauVerlauf = null) {
    if (berechnungen.length === 0) {
        const startJahr = new Date().getFullYear();
        const labels = [];
        for (let i = 0; i <= 30; i++) {
            labels.push(startJahr + i);
        }
        chart.data.labels = labels;
        chart.data.datasets = [];
        
        chart.options.scales.x.ticks.display = false;
        chart.options.scales.y.ticks.display = false;
        
        chart.update('none');
        return;
    }
    
    chart.options.scales.x.ticks.display = true;
    chart.options.scales.y.ticks.display = true;
    
    let maxLaufzeitAlle = Math.max(...berechnungen.map(b => b.parameter.laufzeit));
    if (vorschauVerlauf && vorschauVerlauf.length > 0) {
        const vorschauJahre = vorschauVerlauf[vorschauVerlauf.length - 1].jahr - new Date().getFullYear();
        maxLaufzeitAlle = Math.max(maxLaufzeitAlle, vorschauJahre);
    }
    
    const startJahr = new Date().getFullYear();
    const labels = [];
    for (let i = 0; i <= maxLaufzeitAlle; i++) {
        labels.push(startJahr + i);
    }
    chart.data.labels = labels;
    
    const datasets = berechnungen.map((ber, berIndex) => {
        const istAusgewaehlt = ber.id === ausgewaehlteId;
        const p = ber.parameter;
        const intervallKurz = p.intervall === 'Monatlich' ? 'm' : 
                             p.intervall === 'Vierteljährlich' ? 'v' : 'j';
        
        const label = `${formatCurrency(p.einzahlung)} (${intervallKurz}), ${p.zinssatz}%`;
        
        const data = [];
        for (let i = 0; i <= maxLaufzeitAlle; i++) {
            const jahr = startJahr + i;
            const punkt = ber.verlauf.find(v => v.jahr === jahr);
            data.push(punkt ? punkt.kapital : null);
        }
        
        const farben = ['#06d6a6', '#4a90e2', '#e94b3c'];
        const farbeIndex = berIndex % farben.length;
        const baseFarbe = farben[farbeIndex];
        
        return {
            label: label,
            data: data,
            borderColor: istAusgewaehlt ? baseFarbe : baseFarbe + '55',
            backgroundColor: istAusgewaehlt ? baseFarbe + '33' : baseFarbe + '11',
            borderWidth: istAusgewaehlt && !vorschauVerlauf ? 3 : 2,
            pointRadius: istAusgewaehlt && !vorschauVerlauf ? 4 : 3,
            pointHoverRadius: 6,
            tension: 0.3,
            spanGaps: true,
            berechnungIndex: berIndex  // Index speichern für Legend
        };
    });
    
    if (vorschauVerlauf && vorschauAktiv && ausgewaehlteId) {
        const data = [];
        for (let i = 0; i <= maxLaufzeitAlle; i++) {
            const jahr = startJahr + i;
            const punkt = vorschauVerlauf.find(v => v.jahr === jahr);
            data.push(punkt ? punkt.kapital : null);
        }
        
        datasets.push({
            label: 'Vorschau',
            data: data,
            borderColor: '#ffaa00',
            backgroundColor: '#ffaa0022',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 2,
            pointHoverRadius: 5,
            tension: 0.3,
            spanGaps: true
        });
    }
    
    chart.data.datasets = datasets;
    chart.update('none');
}

// ============ ZURÜCKSETZEN ============
async function zuruecksetzen() {
    const loeschPromises = [];
    for (let i = 1; i <= 3; i++) {
        loeschPromises.push(
            fetch(`${API_BASE}/vergleich/loeschen/${i}`, { method: 'DELETE' })
                .catch(err => console.error(`Fehler beim Löschen von Vergleich ${i}:`, err))
        );
    }
    
    await Promise.all(loeschPromises);
    berechnungen = [];
    
    document.getElementById('zinssatz').value = 3;
    document.getElementById('kontostand').value = 1000;
    document.getElementById('einzahlung').value = 100;
    document.getElementById('laufzeit').value = 10;
    document.getElementById('intervall').value = 'Monatlich';
    document.querySelector('input[name="kontostandTyp"][value="fiktiv"]').checked = true;
    document.getElementById('kontostandEingabe').style.display = 'block';
    document.getElementById('kontenauswahlGruppe').style.display = 'none';
    
    updateSliderLabels();
    
    document.getElementById('ergebnisBox').style.display = 'none';
    
    ausgewaehlteId = null;
    vorschauAktiv = false;
    
    document.getElementById('aktualisierenBtn').style.display = 'none';
    document.getElementById('berechnenBtn').textContent = 'Berechnen (Neu)';
    
    aktualisiereListe();
    aktualisiereChart();
}

// ============ KONTEN LADEN ============
async function ladeKonten() {
    try {
        const response = await fetch(`http://localhost:8000/konten`);
        const konten = await response.json();
        
        if (Array.isArray(konten) && konten.length > 0) {
            kontenListe = konten;
            
            const select = document.getElementById('kontoauswahl');
            select.innerHTML = '<option value="">-- Konto auswählen --</option>';
            
            konten.forEach(konto => {
                const option = document.createElement('option');
                option.value = konto.iban;
                const ibanKurz = konto.iban_kurz || `${konto.iban.substring(0, 4)}...${konto.iban.substring(konto.iban.length - 4)}`;
                option.textContent = `${ibanKurz} - ${formatCurrency(konto.kontostand)}`;
                select.appendChild(option);
            });
            
            console.log(`${konten.length} Konten geladen`);
        } else {
            const select = document.getElementById('kontoauswahl');
            select.innerHTML = '<option value="">Keine Konten gefunden</option>';
            console.log('Keine Konten in Datenbank');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Konten:', error);
        const select = document.getElementById('kontoauswahl');
        select.innerHTML = '<option value="">Fehler beim Laden</option>';
    }
}

// ============ API FUNKTIONEN ============
async function speichereVergleich(dbNummer, verlauf, parameter) {
    try {
        const response = await fetch(`${API_BASE}/vergleich/speichern`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                db_nummer: dbNummer,
                verlauf: verlauf,
                parameter: parameter
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Fehler beim Speichern:', error);
        return { success: false };
    }
}

async function ladeAlleVergleiche() {
    try {
        const response = await fetch(`${API_BASE}/vergleich/alle`);
        const data = await response.json();
        
        if (data.success && data.vergleiche) {
            berechnungen = [];
            Object.keys(data.vergleiche).forEach((key, index) => {
                const v = data.vergleiche[key];
                berechnungen.push({
                    id: Date.now() + index,
                    verlauf: v.verlauf,
                    parameter: v.parameter
                });
            });
            
            if (berechnungen.length > 0) {
                ausgewaehlteId = berechnungen[berechnungen.length - 1].id;
                zeigeErgebnis(berechnungen[berechnungen.length - 1]);
                ladeParameterInsFormular(berechnungen[berechnungen.length - 1]);
                document.getElementById('aktualisierenBtn').style.display = 'block';
                document.getElementById('berechnenBtn').textContent = 'Berechnen (Neu)';
            }
            
            aktualisiereListe();
            aktualisiereChart();
        }
    } catch (error) {
        console.error('Fehler beim Laden:', error);
    }
}

async function loescheVergleich(dbNummer) {
    try {
        const response = await fetch(`${API_BASE}/vergleich/loeschen/${dbNummer}`, {
            method: 'DELETE'
        });
        return await response.json();
    } catch (error) {
        console.error('Fehler beim Löschen:', error);
        return { success: false };
    }
}

async function loescheBerechnungById(id) {
    const index = berechnungen.findIndex(b => b.id === id);
    if (index === -1) return;
    
    const dbNummer = index + 1;
    berechnungen.splice(index, 1);
    
    await loescheVergleich(dbNummer);
    
    if (index < berechnungen.length) {
        for (let i = index; i < berechnungen.length; i++) {
            await speichereVergleich(i + 1, berechnungen[i].verlauf, berechnungen[i].parameter);
        }
    }
    
    if (ausgewaehlteId === id) {
        if (berechnungen.length > 0) {
            ausgewaehlteId = berechnungen[berechnungen.length - 1].id;
            zeigeErgebnis(berechnungen[berechnungen.length - 1]);
            ladeParameterInsFormular(berechnungen[berechnungen.length - 1]);
        } else {
            ausgewaehlteId = null;
            document.getElementById('ergebnisBox').style.display = 'none';
            document.getElementById('aktualisierenBtn').style.display = 'none';
            document.getElementById('berechnenBtn').textContent = 'Berechnen (Neu)';
        }
    }
    
    aktualisiereListe();
    aktualisiereChart();
}

// ============ HILFSFUNKTIONEN ============
function formatCurrency(value) {
    return parseFloat(value).toLocaleString('de-DE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' €';
}
