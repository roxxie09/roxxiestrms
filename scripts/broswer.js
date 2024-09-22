function detectDevTools() {
    const start = performance.now();
    debugger; // Execution will pause here if dev tools are open
    const end = performance.now();

    if (end - start > 100) { // If it takes longer than expected, dev tools are likely open
        window.location.href = "https://roxiestreams.xyz"; // Redirect to homepage
    }
}

setInterval(detectDevTools, 1000);