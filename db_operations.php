<?php
// Database connection function using Singleton pattern
function getDatabaseConnection() {
    static $pdo = null;
    if ($pdo === null) {
        try {
            // Get the current directory of the PHP script
            $dbPath = __DIR__ . '/bookings.db';
            
            // Check if the database file exists
            $isNewDatabase = !file_exists($dbPath);

            // Create the PDO connection to the SQLite database
            $pdo = new PDO("sqlite:$dbPath");
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            // If the database is newly created, create the Booking table
            if ($isNewDatabase) {
                $createTableSQL = "
                    CREATE TABLE IF NOT EXISTS Booking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        status INTEGER NOT NULL
                    );
                ";
                $pdo->exec($createTableSQL);
                error_log("Database and 'Booking' table created successfully.");
            }

        } catch (PDOException $e) {
            die("Database connection failed: " . $e->getMessage());
        }
    }
    return $pdo;
}


function getStatusLabel($status) {
    $statusLabels = [
        0 => 'Pending',
        1 => 'Booked',
        // 2 => 'finished'
    ];
    return $statusLabels[$status] ?? 'Unknown';
}

function deleteBooking($id) {
    try {
        $pdo = getDatabaseConnection();
        $stmt = $pdo->prepare("DELETE FROM Booking WHERE id = :id");
        $stmt->execute([':id' => (int) $id]);
        echo "Booking deleted successfully.";
    } catch (PDOException $e) {
        error_log("Error deleting booking: " . $e->getMessage());
    }
}

// Function to get bookings by status
function getBookingsByStatus($status) {
    try {
        $pdo = getDatabaseConnection();
        if ($status === '' || $status === null) {
            // If $status is empty, fetch all bookings without filtering
            $stmt = $pdo->prepare("SELECT * FROM Booking WHERE date > date('now', '-1 day') ORDER BY date ASC, time ASC");
            $stmt->execute();
        } else {
            // Otherwise, fetch bookings filtered by the given status
            $stmt = $pdo->prepare("SELECT * FROM Booking WHERE status = :status ORDER BY date ASC, time ASC");
            $stmt->execute([':status' => (int) $status]);
        }
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        error_log("Error fetching bookings: " . $e->getMessage());
        return [];
    }
}

// Function to create a booking
function createBooking($date, $time, $status = 0) {
    try {
        $pdo = getDatabaseConnection();
         // Check if a booking with the same date and time already exists
        $checkStmt = $pdo->prepare("SELECT COUNT(*) FROM Booking WHERE date = :date AND time = :time");
        $checkStmt->execute([
            ':date' => $date,
            ':time' => $time
        ]);
        
        $count = $checkStmt->fetchColumn();
        
        if ($count > 0) {
            error_log("Duplicate booking attempt: A booking already exists for date $date and time $time.");
            return; // Exit the function to avoid duplicate entry
        }
        $stmt = $pdo->prepare("INSERT INTO Booking (date, time, status) VALUES (:date, :time, :status)");
        $stmt->execute([
            ':date' => $date,
            ':time' => $time,
            ':status' => (int) $status
        ]);
    } catch (PDOException $e) {
        error_log("Error creating booking: " . $e->getMessage());
    }
}

// Function to handle incoming requests
function handleRequest() {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $action = $_POST['action'] ?? '';
        if ($action === 'create') {
            $date = $_POST['date'] ?? date('Y-m-d');
            $time = $_POST['time'] ?? date('H:i');
            createBooking($date, $time);
            header("Location: index.php");
            exit;
        } elseif ($action === 'delete') {
            $id = $_POST['id'] ?? '';
            if (!empty($id)) {
                deleteBooking($id);
            }
            header("Location: index.php");
            exit;
        }
    } elseif ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['status'])) {
        $status = (int)$_GET['status']; // Casting to integer for security
        $bookings = getBookingsByStatus($status);
        require 'index.php'; // Re-render the page with filtered bookings
        exit;
    }
}
// Call the request handler

handleRequest();