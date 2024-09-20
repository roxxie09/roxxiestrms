document.querySelectorAll('[data-time]').forEach(function(eventCard, index) {
    // Get the event time from the data attribute
    var countDownDate = new Date(eventCard.getAttribute('data-time')).getTime();

    // Update the countdown every 1 second
    setInterval(function() {
        // Get current date and time
        var now = new Date().getTime();

        // Calculate the distance between now and the countdown date
        var distance = countDownDate - now;

        // Time calculations for hours, minutes and seconds
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update the countdown timer display
        var timerElement = document.getElementById(`countdown-timer-${index + 1}`);
        timerElement.innerHTML = hours + "h " + minutes + "m " + seconds + "s ";

        // If the countdown is over, display "LIVE"
        if (distance < 0) {
            clearInterval(this);
            var countdownElement = document.getElementById(`countdown-${index + 1}`);
            countdownElement.innerHTML = "LIVE";
            countdownElement.style.color = "red"; // Change font color to red
            countdownElement.style.fontWeight = "bold"; // Optional: make it bold
            timerElement.innerHTML = ""; // Clear the timer display
        }
    }, 1000);
});
