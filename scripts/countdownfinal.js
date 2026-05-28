// PDT = -7, PST = -8. Change this in November when clocks fall back.
const PST_OFFSET_HOURS = -7;

function parseAsPST(dateStr) {
    // Parse the plain text date as a PST/PDT time, not local time
    var d = new Date(dateStr);
    // Shift from UTC to get the intended PDT time, then back to UTC absolute
    var utcMs = d.getTime() + (d.getTimezoneOffset() * 60000);
    return new Date(utcMs - (PST_OFFSET_HOURS * 3600000));
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
            timeZoneName: 'short'
        });
    });
}

initializeCountdowns();
localizeStartTimes();