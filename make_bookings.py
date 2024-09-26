from session import BookingSession
import sqlite3
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='courtBooker.log',
    level=logging.DEBUG,
    format='%(asctime)s %(name)s {%(filename)s:%(lineno)d} %(levelname)s %(message)s',
    datefmt='%H:%M:%S %d-%M-%Y'
)

logger.info("[Booking Script] Starting court booking script")

nine_days_from_now = datetime.now() + timedelta(days=9)
formatted_date = nine_days_from_now.strftime('%Y-%m-%d')


class Booking(BaseModel):
    id: int
    date: str
    time: str
    status: int


session = BookingSession('credentials.json')

try:
    conn = sqlite3.connect('bookings.db')
    logger.debug("[SQLite] Connected to SQLite database successfully")
except sqlite3.Error as e:
    logger.exception("[SQLite] Failed to connect to SQLite database ->", e)
    raise

c = conn.cursor()
booking_objects = [Booking(id=int(b[0]), date=b[1], time=b[2], status=int(
    b[3])) for b in c.execute('SELECT id, date, time, status FROM Booking WHERE status = 0').fetchall()
    if datetime.now() <= datetime.strptime(b[1], '%Y-%m-%d') <= nine_days_from_now]


for booking in booking_objects:
    try:
        is_booked = session.find_and_book_court(booking.date, booking.time)
    except Exception as e:
        logger.exception(
            f"[Booking Script] Failed trying to book court on {booking.date} at {booking.time} ->", e)
        continue
    if is_booked:
        c.execute('UPDATE Booking SET status = 1 WHERE id = ?', (booking.id,))
        logger.info(
            f"[Booking Script] Updated booking status for booking id {booking.id} to 1 ({booking.date} @ {booking.time})")

conn.commit()
c.close()
conn.close()
logger.debug("[Booking Script] Connection to SQLite database closed")
