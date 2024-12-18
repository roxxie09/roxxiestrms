// After adding the new events
function initializeCountdowns() {
    document.querySelectorAll('[data-time]').forEach(function(eventCard) {
        var countDownDate = new Date(eventCard.getAttribute('data-time')).getTime();
        var endTime = new Date(eventCard.getAttribute('data-end-time')).getTime();
        
        var timerElement = eventCard.querySelector('.countdown-timer');
        var intervalId = setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownDate - now;
            // Calculate days, hours, minutes, and seconds
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            timerElement.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
            if (distance < 0) {
                clearInterval(intervalId);
                timerElement.innerHTML = "LIVE";
                timerElement.style.color = "red"; 
                timerElement.style.fontWeight = "bold"; 
            }
            // Check if the event has ended
            if (now > endTime) {
                clearInterval(intervalId);
                eventCard.remove();
            }
        }, 1000);
    });
}
// Call this function after you add new events to the DOM
initializeCountdowns();