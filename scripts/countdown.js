// Set the date we're counting down to
var countDownDate = new Date("September 19, 2024 05:00:00 GMT-0800").getTime();

// Update the countdown every 1 second
var x = setInterval(function() {
    // Get current date and time
    var now = new Date().getTime();

    // Calculate the distance between now and the countdown date
    var distance = countDownDate - now;

    // Time calculations for hours, minutes and seconds
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Update the countdown timer display
    document.getElementById("countdown-timer").innerHTML = hours + "h " + minutes + "m " + seconds + "s ";

    // If the countdown is over, display "LIVE"
    if (distance < 0) {
        clearInterval(x);
        var countdownElement = document.getElementById("countdown");
        countdownElement.innerHTML = "LIVE";
        countdownElement.style.color = "red"; // Change font color to red
        countdownElement.style.fontWeight = "bold"; // Optional: make it bold
        document.getElementById("countdown-timer").innerHTML = ""; // Clear the timer display
    }
}, 1000);
