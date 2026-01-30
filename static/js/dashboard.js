// Daten beim Laden der Seite abrufen
document.addEventListener("DOMContentLoaded", async () => {
  setupSankeyControls();  // Event-Listener für Monatspfeile
  await loadDashboardData();
});

// Dashboard Daten laden
// Lädt alle Dashboard-Daten (parallel)
async function loadDashboardData() {
  try {
    await Promise.all([
      loadKPIs(),
      loadAccountsPreview(),
      loadTransactionsPreview(),
      loadCategoriesPreview(),
      loadExpensesTrend(),
      loadSankeyChart(),
    ]);
  } catch (error) {
    console.error("Fehler beim Laden der Dashboard-Daten:", error);
    showToast("Fehler beim Laden der Dashboard-Daten", "error");
  }
}

// KPIs laden
// Lädt KPIs (Einnahmen, Ausgaben, Bilanz) für den aktuellen Monat.
// Berechnet auch Trends im Vergleich zum Vormonat.
async function loadKPIs() {
  try {
    // 1. Transaktionen laden (unformatiert für Berechnungen)
    const transResponse = await fetch(`${API_BASE_URL}/transactions?days=365&limit=10000`);
    if (!transResponse.ok) throw new Error("Fehler beim Laden der Transaktionen");
    const allTransactions = await transResponse.json();

    const currentDate = new Date();
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();

    // Berechne vorherigen Monat
    let previousMonth = currentMonth - 1;
    let previousYear = currentYear;
    if (previousMonth < 0) {
      previousMonth = 11;
      previousYear = currentYear - 1;
    }

    // Filtriere Transaktionen des aktuellen Monats
    const monthlyTransactions = allTransactions.filter((t) => {
      const date = new Date(t.buchungstag);
      return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
    });

    // Filtriere Transaktionen des vorherigen Monats
    const previousMonthTransactions = allTransactions.filter((t) => {
      const date = new Date(t.buchungstag);
      return date.getMonth() === previousMonth && date.getFullYear() === previousYear;
    });

    // Berechne Einnahmen und Ausgaben (aktueller Monat)
    const monthlyIncome = monthlyTransactions
      .filter((t) => t.betrag > 0)
      .reduce((sum, t) => sum + t.betrag, 0);

    const monthlyExpenses = Math.abs(
      monthlyTransactions
        .filter((t) => t.betrag < 0)
        .reduce((sum, t) => sum + t.betrag, 0)
    );

    // Berechne Einnahmen und Ausgaben (vorheriger Monat)
    const previousMonthIncome = previousMonthTransactions
      .filter((t) => t.betrag > 0)
      .reduce((sum, t) => sum + t.betrag, 0);

    const previousMonthExpenses = Math.abs(
      previousMonthTransactions
        .filter((t) => t.betrag < 0)
        .reduce((sum, t) => sum + t.betrag, 0)
    );

    const monthlyBalance = monthlyIncome - monthlyExpenses;

    // 2. Setze die KPI-Werte
    document.getElementById("monthlyIncome").textContent = formatCurrency(monthlyIncome);
    document.getElementById("monthlyExpenses").textContent = formatCurrency(monthlyExpenses);
    document.getElementById("monthlyBalance").textContent = formatCurrency(monthlyBalance);

    // 3. Berechne prozentuale Veränderungen zum vorherigen Monat
    // Einkommensveränderung
    const incomeChangeElem = document.getElementById("incomeChange");
    if (previousMonthIncome > 0) {
      const incomeChangePercent = (((monthlyIncome - previousMonthIncome) / previousMonthIncome) * 100).toFixed(1);
      incomeChangeElem.textContent = (monthlyIncome >= previousMonthIncome ? "+" : "") + incomeChangePercent + "%";
      incomeChangeElem.className = monthlyIncome >= previousMonthIncome ? "kpi-change positive" : "kpi-change negative";
    } else {
      incomeChangeElem.textContent = "--";
      incomeChangeElem.className = "kpi-change";
    }

    // Ausgabenveränderung
    const expensesChangeElem = document.getElementById("expensesChange");
    if (previousMonthExpenses > 0) {
      const expensesChangePercent = (((monthlyExpenses - previousMonthExpenses) / previousMonthExpenses) * 100).toFixed(1);
      expensesChangeElem.textContent = (monthlyExpenses <= previousMonthExpenses ? "+" : "") + expensesChangePercent + "%";
      expensesChangeElem.className = monthlyExpenses <= previousMonthExpenses ? "kpi-change positive" : "kpi-change negative";
    } else {
      expensesChangeElem.textContent = "--";
      expensesChangeElem.className = "kpi-change";
    }

    // 4. Bilanz-Indikator
    const balanceChangePercent = document.getElementById("balanceChangePercent");
    if (monthlyBalance >= 0) {
      balanceChangePercent.textContent = "✓ Positiv";
      balanceChangePercent.className = "kpi-change positive";
    } else {
      balanceChangePercent.textContent = "✗ Negativ";
      balanceChangePercent.className = "kpi-change negative";
    }

  } catch (error) {
    console.error("Fehler beim Laden der KPIs:", error);
    showToast("Fehler beim Laden der KPI-Daten", "error");
  }
}

// Konten Preview laden (für KPI-Karte)
/**
 * Lädt eine kleine Vorschau der Konten für die KPI-Karte (als Icons).
 */
async function loadAccountsPreview() {
  try {
    const accounts = await fetchKonten();

    const iconsContainer = document.getElementById("accountsKpiIcons");

    if (!iconsContainer) return;

    iconsContainer.innerHTML = "";

    if (accounts.length === 0) {
      iconsContainer.innerHTML = '<span style="color: #888; font-size: 0.8rem;">Noch keine Konten</span>';
      return;
    }

    // Zeige alle Konten als Icons
    accounts.forEach((account) => {
      const icon = document.createElement("div");
      icon.className = "kpi-account-icon";
      icon.title = account.kontoname;
      icon.textContent = getAccountIcon(account.kontotyp.toLowerCase());
      iconsContainer.appendChild(icon);
    });

  } catch (error) {
    console.error("Fehler beim Laden der Konten:", error);
  }
}

// Lädt letzte Transaktionen für Dashboard-Vorschau.
async function loadTransactionsPreview() {
  try {
    const [transactionsRes, kontos] = await Promise.all([
      fetch(`${API_BASE_URL}/transactions?days=30`),
      fetchKonten(),
    ]);

    let transactions = await transactionsRes.json();

    // Map für Kontonamen erstellen
    const konto_map = {};
    kontos.forEach(k => {
      konto_map[k.id] = k.kontoname;
    });

    // Nach Datum sortieren (neueste zuerst)
    transactions.sort((a, b) => new Date(b.buchungstag) - new Date(a.buchungstag));

    // Nur die ersten 5 Transaktionen
    const previewTransactions = transactions.slice(0, 5);

    const container = document.getElementById("transactionsPreview");
    container.innerHTML = "";

    if (previewTransactions.length === 0) {
      container.innerHTML = '<p style="color: #888; text-align: center;">Noch keine Transaktionen vorhanden</p>';
      return;
    }

    previewTransactions.forEach((transaction) => {
      const item = document.createElement("div");
      item.className = "transaction-preview-item";

      const isPositive = transaction.betrag > 0;
      const icon = isPositive ? "💰" : "💸";
      const amountClass = isPositive ? "positive" : "negative";
      const amountText = isPositive ? `+${formatCurrency(transaction.betrag)}` : formatCurrency(transaction.betrag);

      const date = formatDateDE(transaction.buchungstag, { pad: false });
      const kontoName = konto_map[transaction.konto_id] || "Konto";

      item.innerHTML = `
        <div class="transaction-preview-info">
          <div class="transaction-preview-icon">${icon}</div>
          <div class="transaction-preview-details">
            <h4>${transaction.beguenstigter || "Unbekannt"}</h4>
            <p>${date} • ${kontoName}</p>
          </div>
        </div>
        <div class="transaction-preview-amount ${amountClass}">${amountText}</div>
      `;

      container.appendChild(item);
    });

  } catch (error) {
    console.error("Fehler beim Laden der Transaktionen:", error);
  }
}

// Lädt Top Kategorien (Ausgaben) der letzten 30 Tage.
async function loadCategoriesPreview() {
  try {
    const [transactionsRes, kategorien] = await Promise.all([
      fetch(`${API_BASE_URL}/transactions?days=30`),
      fetchCategories(),
    ]);

    const transactions = await transactionsRes.json();

    // Berechne das Datum vor 30 Tagen
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));

    // Summen pro Kategorie berechnen (nur letzte 30 Tage, nur Ausgaben)
    const categorySums = {};
    transactions
      .filter((t) => {
        const transDate = new Date(t.buchungstag);
        return t.betrag < 0 && transDate >= thirtyDaysAgo;
      })
      .forEach((t) => {
        // Nur kategorisierte Transaktionen zählen
        let catName = null;

        if (t.kategorie_id && kategorien.length > 0) {
          const kat = kategorien.find(k => k.id === t.kategorie_id);
          if (kat) {
            catName = kat.name;
          }
        }

        // Nur hinzufügen, wenn eine echte Kategorie vorhanden ist
        if (catName) {
          if (!categorySums[catName]) {
            categorySums[catName] = 0;
          }
          categorySums[catName] += Math.abs(t.betrag);
        }
      });

    // Top 5 Kategorien
    const topCategories = Object.entries(categorySums)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    const container = document.getElementById("categoriesPreview");
    container.innerHTML = "";

    if (topCategories.length === 0) {
      container.innerHTML = '<p style="color: #888; text-align: center;">Keine kategorisierten Ausgaben in den letzten 30 Tagen</p>';
      return;
    }

    const maxAmount = topCategories[0][1];

    topCategories.forEach(([name, amount]) => {
      const percentage = (amount / maxAmount) * 100;

      const item = document.createElement("div");
      item.className = "category-preview-item";

      item.innerHTML = `
        <div class="category-preview-header">
          <span class="category-preview-name">${name}</span>
          <span class="category-preview-amount">${formatCurrency(amount)}</span>
        </div>
        <div class="category-preview-bar">
          <div class="category-preview-fill" style="width: ${percentage}%"></div>
        </div>
      `;

      container.appendChild(item);
    });

  } catch (error) {
    console.error("Fehler beim Laden der Kategorien:", error);
  }
}

// Lädt Diagrammdaten für den Einnahmen/Ausgaben-Verlauf der letzten 6 Monate.
async function loadExpensesTrend() {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions?days=180&limit=10000`);
    const transactions = await response.json();

    // Letzte 6 Monate
    const months = [];
    const expenses = [];
    const income = [];

    for (let i = 5; i >= 0; i--) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      const month = date.getMonth();
      const year = date.getFullYear();

      const monthName = date.toLocaleDateString("de-DE", { month: "short" });
      months.push(monthName);

      // Ausgaben berechnen
      const monthExpenses = transactions
        .filter((t) => {
          const tDate = new Date(t.buchungstag);
          return (
            tDate.getMonth() === month &&
            tDate.getFullYear() === year &&
            t.betrag < 0
          );
        })
        .reduce((sum, t) => sum + Math.abs(t.betrag), 0);

      expenses.push(monthExpenses);

      // Einnahmen berechnen
      const monthIncome = transactions
        .filter((t) => {
          const tDate = new Date(t.buchungstag);
          return (
            tDate.getMonth() === month &&
            tDate.getFullYear() === year &&
            t.betrag > 0
          );
        })
        .reduce((sum, t) => sum + t.betrag, 0);

      income.push(monthIncome);
    }

    const ctx = document.getElementById("expensesTrendChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: months,
        datasets: [
          {
            label: "Einnahmen",
            data: income,
            borderColor: "#06d6a6",
            backgroundColor: "rgba(6, 214, 166, 0.1)",
            tension: 0.4,
            fill: true,
            pointBackgroundColor: "#06d6a6",
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: "Ausgaben",
            data: expenses,
            borderColor: "#ff6b6b",
            backgroundColor: "rgba(255, 107, 107, 0.1)",
            tension: 0.4,
            fill: true,
            pointBackgroundColor: "#ff6b6b",
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              color: "#888",
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            backgroundColor: "#2a2a2a",
            titleColor: "#fff",
            bodyColor: "#fff",
            borderColor: "#444",
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: "#2a2a2a",
              drawBorder: false,
            },
            ticks: {
              color: "#888",
            },
          },
          y: {
            grid: {
              color: "#2a2a2a",
              drawBorder: false,
            },
            ticks: {
              color: "#888",
              callback: function (value) {
                return formatCurrency(value);
              },
            },
          },
        },
      },
    });

  } catch (error) {
    console.error("Fehler beim Laden des Ausgaben-Trends:", error);
  }
}

// ==================== SANKEY DIAGRAMM ====================

// Aktueller Monat für Sankey (global)
let sankeyCurrentYear = new Date().getFullYear();
let sankeyCurrentMonth = new Date().getMonth() + 1; // 1-12

// Monatslabel aktualisieren
// Aktualisiert das Text-Label für den aktuellen Sankey-Monat (z.B. "Januar 2026").
function updateSankeyMonthLabel() {
  const label = document.getElementById('sankeyMonthLabel');
  if (label) {
    label.textContent = `${MONTH_NAMES_DE[sankeyCurrentMonth - 1]} ${sankeyCurrentYear}`;
  }
}

// Sankey-Diagramm laden
// Lädt Sankey-Diagramm für gewählten Monat und Jahr.
async function loadSankeyChart() {
  const sankeyElement = document.getElementById('sankeyChart');
  if (!sankeyElement) return;

  // Monatslabel aktualisieren
  updateSankeyMonthLabel();

  // Container leeren (wichtig für Monatswechsel)
  sankeyElement.innerHTML = '<div style="text-align: center; color: #888; padding: 40px;">⏳ Laden...</div>';

  try {
    // Lade Sankey-Daten für den ausgewählten Monat
    const response = await fetch(`${API_BASE_URL}/transactions/sankey-data?year=${sankeyCurrentYear}&month=${sankeyCurrentMonth}`);
    const data = await response.json();

    // Prüfe ob Daten vorhanden
    if (!data.nodes || data.nodes.length === 0) {
      sankeyElement.innerHTML = `<div style="text-align: center; color: #888; padding: 40px;">Keine Ausgaben im ${MONTH_NAMES_DE[sankeyCurrentMonth - 1]} ${sankeyCurrentYear}</div>`;
      return;
    }

    // Extrahiere Arrays für Plotly aus den Backend-Daten
    const nodeLabels = data.nodes.map(n => n.label);
    const nodeColors = data.nodes.map(n => n.color);

    const sources = data.links.map(l => l.source);
    const targets = data.links.map(l => l.target);
    const values = data.links.map(l => l.value);
    const linkColors = data.links.map(l => l.color);

    // Plotly Sankey erstellen
    const trace = {
      type: 'sankey',
      orientation: 'h',
      node: {
        pad: 15,
        thickness: 30,
        line: { color: '#444', width: 0.5 },
        label: nodeLabels,
        color: nodeColors,
        hovertemplate: '<b>%{label}</b><br>%{value:,.2f} €<extra></extra>'
      },
      link: {
        source: sources,
        target: targets,
        value: values,
        color: linkColors,
        hovertemplate: '%{source.label} → %{target.label}<br><b>%{value:,.2f} €</b><extra></extra>'
      }
    };

    const layout = {
      font: { size: 13, color: '#ccc', family: 'Arial, sans-serif' },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: { l: 10, r: 10, t: 10, b: 10 }
    };

    const config = {
      responsive: true,
      displayModeBar: false
    };

    // Container leeren vor dem Rendern
    sankeyElement.innerHTML = '';
    Plotly.newPlot(sankeyElement, [trace], layout, config);
    console.log(`✓ Sankey-Diagramm geladen (${MONTH_NAMES_DE[sankeyCurrentMonth - 1]} ${sankeyCurrentYear}, ${data.category_count} Kategorien, ${formatCurrency(data.total_expenses)})`);

  } catch (error) {
    console.error('✗ Fehler beim Laden des Sankey-Diagramms:', error);
    sankeyElement.innerHTML = '<div style="text-align: center; color: #ff6b6b; padding: 40px;">Fehler beim Laden des Diagramms</div>';
  }
}

// Ändert Monat für Sankey-Diagramm
function changeSankeyMonth(delta) {
  sankeyCurrentMonth += delta;

  // Jahr wechseln wenn nötig
  if (sankeyCurrentMonth > 12) {
    sankeyCurrentMonth = 1;
    sankeyCurrentYear++;
  } else if (sankeyCurrentMonth < 1) {
    sankeyCurrentMonth = 12;
    sankeyCurrentYear--;
  }

  // Diagramm neu laden
  loadSankeyChart();
}

// Richtet Event-Listener für die Monats-Navigation beim Sankey-Diagramm ein.
function setupSankeyControls() {
  const prevBtn = document.getElementById('sankeyPrevMonth');
  const nextBtn = document.getElementById('sankeyNextMonth');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => changeSankeyMonth(-1));
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => changeSankeyMonth(1));
  }
}
