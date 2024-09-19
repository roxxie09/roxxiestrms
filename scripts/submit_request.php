<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $type = $_POST['type'];
    $title = $_POST['eventname'];
    $summary = $_POST['eventchannel'];

    if ($type === 'bugreport') {
        $severity = $_POST['severity'];
        // Handle bug report logic (e.g., save to database, send email, etc.)
    } else {
        // Handle suggestion logic
    }
    
    // Example: send an email or save the report/suggestion
    // mail($to, $subject, $message);
}
?>
