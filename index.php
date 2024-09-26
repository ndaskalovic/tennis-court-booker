<?php
require_once "db_operations.php";
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }

        .container {
            width: 80%;
            margin: auto;
            text-align: center;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th,
        td {
            padding: 10px;
            border: 1px solid #ddd;
        }

        th {
            background-color: #f4f4f4;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>Booking System</h1>

        <!-- Form to create a new booking -->
        <h2>Create New Booking</h2>
        <form action="db_operations.php" method="post">
            <input type="hidden" name="action" value="create">
            <label for="date">Date:</label>
            <input type="date" id="date" name="date" required>

            <label for="time">Time:</label>
            <input type="time" id="time" name="time" required>

            <button type="submit">Create Booking</button>
        </form>

        <!-- Filter bookings by status dropdown -->
        <h2>View Bookings</h2>
        <form action="" method="get">
            <label for="status_filter">Filter by Status: </label>
            <select name="status" id="status_filter" onchange="this.form.submit()">
                <option value="">All</option>
                <option value="0" <?=isset($_GET['status']) && $_GET['status']==="0" ? 'selected' : '' ?>>Pending</option>
                <option value="1" <?=isset($_GET['status']) && $_GET['status']==="1" ? 'selected' : '' ?>>Booked</option>
                <!-- <option value="2" <?=isset($_GET['status']) && $_GET['status']==="2" ? 'selected' : '' ?>>Finished</option> -->
            </select>
        </form>

        <!-- Display bookings in a table -->
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach (getBookingsByStatus($_GET['status'] ?? '') as $booking): ?>
                <tr>
                    <td>
                        <?= htmlspecialchars($booking['date']); ?>
                    </td>
                    <td>
                        <?= htmlspecialchars($booking['time']); ?>
                    </td>
                    <td>
                        <?= htmlspecialchars(getStatusLabel($booking['status'])); ?>
                    </td>
                     <td>
                <!-- Form to delete the booking -->
                <form action="db_operations.php" method="post" style="display:inline;">
                    <input type="hidden" name="action" value="delete">
                    <input type="hidden" name="id" value="<?= $booking['id']; ?>">
                    <button type="submit" onclick="return confirm('Are you sure you want to delete this booking?');">
                        Delete
                    </button>
                </form>
            </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>

</html>