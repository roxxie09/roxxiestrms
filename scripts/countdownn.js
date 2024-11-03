document.addEventListener('DOMContentLoaded', function() {
    const countdownElements = document.querySelectorAll('.countdown-timer');

    countdownElements.forEach(timer => {
        const eventTime = new Date(timer.parentElement.parentElement.getAttribute('data-time')).getTime();

        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = eventTime - now;

            // Time calculations
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            if (distance < 0) {
                timer.innerHTML = "Started";
                clearInterval(interval); // Clear the interval if the countdown is finished
            } else {
                timer.innerHTML = `${hours}h ${minutes}m ${seconds}s`;
            }
        };

        updateCountdown(); // Initial call
        const interval = setInterval(updateCountdown, 1000); // Update every second
    });
});
