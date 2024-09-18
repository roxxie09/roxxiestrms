const countdownElement = document.getElementById('countdown');

function updateCountdown() {
    const eventDate = new Date('2024-09-17T23:26:00-08:00'); // Change this to your desired time
    const now = new Date();
    const timeDiff = eventDate - now;

    if (timeDiff > 0) {
        const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);
        
        countdownElement.innerHTML = `${hours}h ${minutes}m ${seconds}s`;
    } else {
        countdownElement.innerHTML = "Event has started!";
    }
}

setInterval(updateCountdown, 1000);
