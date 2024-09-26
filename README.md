# Tennis Court Booking System
This repo contains a small and lightweight full-stack application I made to automate the booking of tennis court at my local tennis club since they are in high demand. It makes use of API endpoints I reverse-engineering from their mobile app.

## Stack
- PHP for handling web equest, building DOM elements and managing the database
- SQLite for a lightweight file-based database
- HTML and CSS for the (rather simple) frontend
- Python for the actual booking through the API (uses curl_cffi for TLS spoofing)
- Cron for scheduling when to try and book courts

## Running

### Webserver

Also make sure to have php and an sqlite php plugin installed. On linux you can install these with
```bash
sudo apt install php-sqlite3 php-cli
```
You must have `php` installed to run the webserver with
```bash
php -S localhost:8000
```
The database will automatically be created with the correct tables once you access the app at `localhost:8000`.

### Scheduled Booking
The Python requirements can be found in [requirements.txt](requirements.txt). I suggest running this in a virtual environment or with conda. There is an [example bash script](example_bash_script.sh) included to automate this. There is also an [example crontab entry](example_crontab) which you can use to run the booking system at a set time. The booking system will take all of the requested booking times and dates and try to match them with an available court and book it.

## Logging

Logging for the booking system is set up with the `logging` Python package and will be saved to a `courtBooker.log` file.

## Credentials

You must add a `credentials.json` file in the root of this directory with the username and password for accessing the API in the following format
```json
{
    "username": "username",
    "password": "password"
}
```

##

The actual API URLS cannot be found in this repo.
