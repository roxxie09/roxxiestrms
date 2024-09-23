document.querySelectorAll('[data-time]').forEach(function(eventCard, index) {
    var countDownDate = new Date(eventCard.getAttribute('data-time')).getTime();
    var endTime = new Date(eventCard.getAttribute('data-end-time')).getTime();

    var intervalId = setInterval(function() {
        var now = new Date().getTime();
        var distance = countDownDate - now;

        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        var timerElement = document.getElementById(`countdown-timer-${index + 1}`);
        timerElement.innerHTML = hours + "h " + minutes + "m " + seconds + "s ";

        if (distance < 0) {
            clearInterval(intervalId);
            var countdownElement = document.getElementById(`countdown-${index + 1}`);
            countdownElement.innerHTML = "LIVE";
            countdownElement.style.color = "red"; 
            countdownElement.style.fontWeight = "bold"; 
            timerElement.innerHTML = ""; 
        }

        // Check if the event has ended
        if (now > endTime) {
            clearInterval(intervalId);
            eventCard.remove();
        }
    }, 1000);
});
