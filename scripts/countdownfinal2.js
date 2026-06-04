// PDT = -7, PST = -8. Change this in November when clocks fall back.
const PST_OFFSET_HOURS = -7; // PDT = -7, PST = -8 in winter

function parseAsPST(dateStr) {
    var d = new Date(dateStr);
    // Build an ISO string with the explicit offset so no shifting is needed
    var year = d.getFullYear();
    var month = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    var hours = String(d.getHours()).padStart(2, '0');
    var minutes = String(d.getMinutes()).padStart(2, '0');
    var offset = PST_OFFSET_HOURS >= 0
        ? '+' + String(PST_OFFSET_HOURS).padStart(2, '0') + ':00'
        : '-' + String(Math.abs(PST_OFFSET_HOURS)).padStart(2, '0') + ':00';
    return new Date(`${year}-${month}-${day}T${hours}:${minutes}:00${offset}`);
}
function initializeCountdowns() {
    document.querySelectorAll('.countdown-timer').forEach(function(timerElement) {
        // Find the sibling start-time <td> in the same row
        var row = timerElement.closest('tr');
        var timeTd = row ? row.querySelector('.event-start-time') : null;
        var startStr = timeTd ? timeTd.textContent.trim() : timerElement.getAttribute('data-start');

        var countDownDate = parseAsPST(startStr).getTime();

        setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownDate - now;

            if (distance >= 0) {
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                timerElement.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s";
                timerElement.style.color = "#ff0000";
                timerElement.style.fontWeight = "bold";
            } else {
                timerElement.innerHTML = "LIVE";
                timerElement.style.color = "red";
                timerElement.style.fontWeight = "bold";
            }
        }, 1000);
    });
}

function localizeStartTimes() {
    document.querySelectorAll('.event-start-time').forEach(function(cell) {
        var originalText = cell.textContent.trim();
        if (!originalText) return;
        var date = parseAsPST(originalText);
        cell.textContent = date.toLocaleString([], {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
        });
    });
}

initializeCountdowns();
localizeStartTimes();