<?php
// Set the log file path
$log_file = 'messages.log';

// Function to log messages to file
function log_message($message) {
    global $log_file;
    $date = date('Y-m-d H:i:s');
    file_put_contents($log_file, "$date - $message\n", FILE_APPEND);
}

if (isset($_GET['new_message'])) {
    $message = $_GET['new_message'];
    log_message($message);
} else {
    $today = date('Y-m-d');
    $lines = file($log_file);
    foreach ($lines as $line) {
        if (strpos($line, $today) !== false) {
            echo $line;
            echo "<br>";
        }
    }
}
?>