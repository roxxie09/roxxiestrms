<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $type = $_POST['type'];
    $eventname = $_POST['eventname'];
    $eventchannel = $_POST['eventchannel'];
    $severity = $_POST['severity'] ?? null; // This will be null if severity is not set

    // Here you can process the data, e.g., save it to a database or send an email

    // For demonstration, we'll just echo the received data
    echo "Type: $type<br>";
    echo "Title: $eventname<br>";
    echo "Summary: $eventchannel<br>";
    if ($severity) {
        echo "Severity: $severity<br>";
    }

    // You can redirect or display a success message
    // header("Location: success_page.php"); // Redirect example
}
?>
