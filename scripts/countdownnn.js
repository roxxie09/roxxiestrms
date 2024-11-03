// countdown.js

let interval; // Declare the variable at the top

function updateCountdown() {
    // Check if interval is already set, if so clear it
    if (interval) {
        clearInterval(interval);
    }
    
    // Your countdown logic here
    const countdownElements = document.querySelectorAll('.countdown-timer');
    countdownElements.forEach(element => {
        // Your logic to calculate the remaining time
        // ...
    });

    // Set the interval for countdown updates
    interval = setInterval(updateCountdown, 1000); // Call updateCountdown every second
}

// Call the updateCountdown function initially to start the countdown
document.addEventListener('DOMContentLoaded', () => {
    updateCountdown();
});
