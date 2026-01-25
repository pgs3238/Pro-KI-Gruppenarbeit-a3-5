// API Base URL
const API_BASE_URL = "http://localhost:8000";

// Toast Notification Funktion
function showToast(message, type = "success") {
  const toastContainer = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 10000);
}

// Daten beim Laden der Seite abrufen
document.addEventListener("DOMContentLoaded", async () => {
  await loadDashboardData();
});

// Dashboard Daten laden
async function loadDashboardData() {
  try {
    await Promise.all([
      loadKPIs(),
      loadAccountsPreview(),
      loadTransactionsPreview(),
      loadCategoriesPreview(),
      loadExpensesTrend(),
    ]);
  } catch (error) {
    console.error("Fehler beim Laden der Dashboard-Daten:", error);
    showToast("Fehler beim Laden der Dashboard-Daten", "error");
  }
}

// KPIs laden
async function loadKPIs() {
  try {
    // Konten laden für Gesamtguthaben
    const accountsResponse = await fetch(`${API_BASE_URL}/konten`);
    const accounts = await accountsResponse.json();
    
    const totalBalance = accounts.reduce((sum, acc) => sum + acc.kontostand, 0);
    document.getElementById("totalBalance").textContent = formatCurrency(totalBalance);
    
    // Balance Change berechnen (Beispielwert, könnte aus Historie berechnet werden)
    const balanceChangeElem = document.getElementById("balanceChange");
    balanceChangeElem.textContent = "+5,2%";
    balanceChangeElem.className = "kpi-change positive";

    // Transaktionen für aktuellen Monat laden
    const transactionsResponse = await fetch(`${API_BASE_URL}/transaktionen`);
    const transactions = await transactionsResponse.json();
    
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    const monthlyTransactions = transactions.filter((t) => {
      const date = new Date(t.buchungstag);
      return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
    });

    const monthlyIncome = monthlyTransactions
      .filter((t) => t.betrag > 0)
      .reduce((sum, t) => sum + t.betrag, 0);
    
    const monthlyExpenses = Math.abs(
      monthlyTransactions
        .filter((t) => t.betrag < 0)
        .reduce((sum, t) => sum + t.betrag, 0)
    );
    
    const monthlyBalance = monthlyIncome - monthlyExpenses;

    document.getElementById("monthlyIncome").textContent = formatCurrency(monthlyIncome);
    document.getElementById("monthlyExpenses").textContent = formatCurrency(monthlyExpenses);
    document.getElementById("monthlyBalance").textContent = formatCurrency(monthlyBalance);

    // Change indicators
    const balanceChangePercent = document.getElementById("balanceChangePercent");
    if (monthlyBalance >= 0) {
      balanceChangePercent.textContent = "Positiv";
      balanceChangePercent.className = "kpi-change positive";
    } else {
      balanceChangePercent.textContent = "Negativ";
      balanceChangePercent.className = "kpi-change negative";
    }

  } catch (error) {
    console.error("Fehler beim Laden der KPIs:", error);
  }
}

// Konten Preview laden
async function loadAccountsPreview() {
  try {
    const response = await fetch(`${API_BASE_URL}/konten`);
    const accounts = await response.json();
    
    // Nur die ersten 3 Konten anzeigen
    const previewAccounts = accounts.slice(0, 3);
    
    const container = document.getElementById("accountsPreview");
    container.innerHTML = "";

    if (previewAccounts.length === 0) {
      container.innerHTML = '<p style="color: #888; text-align: center;">Noch keine Konten vorhanden</p>';
      return;
    }

    previewAccounts.forEach((account) => {
      const accountItem = document.createElement("div");
      accountItem.className = "account-preview-item";
      
      const icon = getAccountIcon(account.typ);
      
      accountItem.innerHTML = `
        <div class="account-preview-info">
          <div class="account-preview-icon">${icon}</div>
          <div class="account-preview-details">
            <h4>${account.name}</h4>
            <p>${account.typ}</p>
          </div>
        </div>
        <div class="account-preview-balance">${formatCurrency(account.kontostand)}</div>
      `;
      
      container.appendChild(accountItem);
    });

  } catch (error) {
    console.error("Fehler beim Laden der Konten:", error);
  }
}

// Transaktionen Preview laden
async function loadTransactionsPreview() {
  try {
    const response = await fetch(`${API_BASE_URL}/transaktionen`);
    let transactions = await response.json();
    
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
      
      const date = new Date(transaction.buchungstag).toLocaleDateString("de-DE");
      
      item.innerHTML = `
        <div class="transaction-preview-info">
          <div class="transaction-preview-icon">${icon}</div>
          <div class="transaction-preview-details">
            <h4>${transaction.beguenstigter || "Unbekannt"}</h4>
            <p>${date} • ${transaction.konto_name || "Konto"}</p>
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

// Kategorien Preview laden
async function loadCategoriesPreview() {
  try {
    const [transactionsRes, categoriesRes] = await Promise.all([
      fetch(`${API_BASE_URL}/transaktionen`),
      fetch(`${API_BASE_URL}/kategorien`),
    ]);
    
    const transactions = await transactionsRes.json();
    const categories = await categoriesRes.json();
    
    // Nur Ausgaben-Kategorien
    const expenseCategories = categories.filter((c) => c.typ === "ausgabe");
    
    // Summen pro Kategorie berechnen
    const categorySums = {};
    transactions
      .filter((t) => t.betrag < 0)
      .forEach((t) => {
        const catName = t.kategorie_name || "Sonstiges";
        if (!categorySums[catName]) {
          categorySums[catName] = 0;
        }
        categorySums[catName] += Math.abs(t.betrag);
      });
    
    // Top 5 Kategorien
    const topCategories = Object.entries(categorySums)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
    
    const container = document.getElementById("categoriesPreview");
    container.innerHTML = "";

    if (topCategories.length === 0) {
      container.innerHTML = '<p style="color: #888; text-align: center;">Noch keine Ausgaben vorhanden</p>';
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

// Ausgaben Trend Chart laden
async function loadExpensesTrend() {
  try {
    const response = await fetch(`${API_BASE_URL}/transaktionen`);
    const transactions = await response.json();
    
    // Letzte 6 Monate
    const months = [];
    const expenses = [];
    
    for (let i = 5; i >= 0; i--) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      const month = date.getMonth();
      const year = date.getFullYear();
      
      const monthName = date.toLocaleDateString("de-DE", { month: "short" });
      months.push(monthName);
      
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
    }

    const ctx = document.getElementById("expensesTrendChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: months,
        datasets: [
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
            display: false,
          },
          tooltip: {
            backgroundColor: "#2a2a2a",
            titleColor: "#fff",
            bodyColor: "#fff",
            borderColor: "#444",
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function (context) {
                return formatCurrency(context.parsed.y);
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

// Helper Funktionen
function formatCurrency(amount) {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
  }).format(amount);
}

function getAccountIcon(typ) {
  const icons = {
    girokonto: "🏦",
    sparkonto: "💰",
    kreditkarte: "💳",
    depot: "📈",
    bargeld: "💵",
  };
  return icons[typ] || "🏦";
}
