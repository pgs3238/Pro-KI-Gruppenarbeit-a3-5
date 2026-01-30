// ==================== KALENDER FUNKTIONEN ====================

// Setzt aktuelles Datum als Standardwert
function setCurrentDate() {
    const datumInput = document.getElementById('datumInput');
    if (!datumInput) return;

    const today = new Date();
    window.selectedDate = today;
    window.currentMonth = new Date(today);
    datumInput.value = formatDateDE(today, { pad: true });
}

// Schaltet Kalender-Sichtbarkeit um
function toggleCalendar() {
    const calendar = document.getElementById('customCalendar');
    if (!calendar) return;
    calendar.style.display = calendar.style.display === 'none' ? 'block' : 'none';
    if (calendar.style.display === 'block') {
        renderCalendar();
    }
}

// Wechselt Kalender-Monat (direction: -1 oder +1)
function changeMonth(direction) {
    if (!window.currentMonth) window.currentMonth = new Date();
    window.currentMonth.setMonth(window.currentMonth.getMonth() + direction);
    renderCalendar();
}

// Rendert den Kalender für den aktuellen Monat
function renderCalendar() {
    if (!window.currentMonth) window.currentMonth = new Date();

    const year = window.currentMonth.getFullYear();
    const month = window.currentMonth.getMonth();

    // Update header
    const monthYear = document.getElementById('calendarMonthYear');
    if (monthYear) monthYear.textContent = `${MONTH_NAMES_DE[month]} ${year}`;

    // Calculate days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;

    const calendarDays = document.getElementById('calendarDays');
    if (!calendarDays) return;

    calendarDays.innerHTML = '';

    // Empty cells for days before month starts
    for (let i = 0; i < adjustedFirstDay; i++) {
        calendarDays.innerHTML += '<span class="calendar-day empty"></span>';
    }

    // Days of month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        const isSelected = day === (window.selectedDate?.getDate?.()) && month === window.selectedDate?.getMonth?.() && year === window.selectedDate?.getFullYear?.();
        const classes = `calendar-day${isToday ? ' today' : ''}${isSelected ? ' selected' : ''}`;
        calendarDays.innerHTML += `<span class="${classes}" onclick="selectDate(${day})">${day}</span>`;
    }
}

// Wählt ein Datum aus und aktualisiert Input
function selectDate(day) {
    if (!window.currentMonth) window.currentMonth = new Date();
    window.selectedDate = new Date(window.currentMonth.getFullYear(), window.currentMonth.getMonth(), day);
    const formattedDate = formatDateDE(window.selectedDate, { pad: true });
    const datumInput = document.getElementById('datumInput');
    if (datumInput) datumInput.value = formattedDate;
    const calendar = document.getElementById('customCalendar');
    if (calendar) calendar.style.display = 'none';
}
