function initializeCountdowns() {
    document.querySelectorAll('.countdown-timer').forEach(function(timerElement) {
        var countDownDate = new Date(timerElement.getAttribute('data-start')).getTime();
        var endTime = new Date(timerElement.getAttribute('data-end')).getTime();

        var intervalId = setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownDate - now;

            if (distance >= 0) {
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                timerElement.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
                timerElement.style.color = "#ff0000";
                timerElement.style.fontWeight = "bold";
            } else if (now <= endTime) {
                timerElement.innerHTML = "LIVE";
                timerElement.style.color = "red";
                timerElement.style.fontWeight = "bold";
            } else {
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
