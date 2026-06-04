function initializeCountdowns() {
    document.querySelectorAll('.countdown-timer').forEach(function(timerElement) {
        var countDownDate = new Date(timerElement.getAttribute('data-start')).getTime();
        var endTime = new Date(timerElement.getAttribute('data-end')).getTime();

        var intervalId = setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownDate - now;

            if (distance >= 0) {
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                clearInterval(intervalId);
                timerElement.innerHTML = "ENDED";
                timerElement.style.color = "gray";
                timerElement.style.fontWeight = "normal";
            }

            if (now > endTime) {
                clearInterval(intervalId);
                // Optionally hide or remove event rows here if needed
            }

        }, 1000);
    });
}

initializeCountdowns();
