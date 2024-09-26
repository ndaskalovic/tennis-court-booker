from curl_cffi import requests
from datetime import datetime
import json
import logging
from urls import (
    LOGIN_URL,
    COURTS_URL,
    SINGLE_COURT_URL,
    RECENT_PLAYERS_URL,
    BOOKING_URL,
    CONFIRM_URL
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='courtBooker.log',
    level=logging.DEBUG,
    format='%(asctime)s %(name)s {%(filename)s:%(lineno)d} %(levelname)s %(message)s',
    datefmt='%H:%M:%S %d-%M-%Y'
)

HARD_COURTS = [
    10470,
    10471,
    10472,
    16704,
    10473
]

courts_codes_reverse = {
    1388: 1,
    1603: 2,
    1604: 3,
    1605: 4,
    10465: 5,
    10467: 6,
    10468: 7,
    10469: 8,
    10470: 9,
    10471: 10,
    10472: 11,
    10473: 12,
}


class BookingSession:
    def __init__(self, credentials: str) -> None:
        with open(credentials) as f:
            creds = json.load(f)
        self._credsfilename = credentials
        self._username = creds['username']
        self._password = creds['password']
        self._token = creds.get("token", None)
        self._encodedContactId = creds.get("encodedContactId", None)

        accessTime = datetime.strptime(
            creds.get('accessTime', "01/01/1970 00:00:00"), "%d/%m/%Y %H:%M:%S")
        if (datetime.now() - accessTime).total_seconds() > 3600 or self._token is None:
            self._login()
        else:
            logger.info("[Login] Skipping login - tokens still valid")
        self.headers = {"x-auth-token": self._token}

    def _login(self) -> dict:
        payload = {
            "username": self._username,
            "password": self._password
        }
        response = requests.post(LOGIN_URL, json=payload, impersonate="chrome")
        if response.status_code == 200:
            self._encodedContactId = response.json()['encodedContactId']
            self._token = response.json()['token']
            self._save_credentials()
            logger.info(f"[Login] Logged in successfully")
            return response.json()
        logger.error(
            f"[Login] Failed to login, response={response.status_code}")
        logger.debug(f"[Login] {response.content}")
        raise Exception("Could not login",
                        response.status_code, response.content)

    def _save_credentials(self) -> None:
        with open(self._credsfilename, 'r+') as f:
            data = json.load(f)
            data['encodedContactId'] = self._encodedContactId
            data['token'] = self._token
            data['accessTime'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            logger.info("[Login] Saved new credentials")

    def _get_courts(self, date: str) -> dict:
        '''
        Returns:
        [
            {"courtId": 10465, "duration": 60, "startTime": "14:00"},
            ...
       ]
        '''
        url = COURTS_URL.format(
            date=date, encodedContactId=self._encodedContactId)
        response = self._get(url)
        logger.info(f"[Get Courts] Fetched courts for {date}")
        return response.json()['slots']

    def _check_court(self, date: str, time: str, courtId: int) -> dict:
        '''
        Returns:
        {
            "bookedMemberEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookedByEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookingReference": "REF-C3C7619-C1EB",
            "date": "2024-09-30",
            "details": {
                "courtId": 10470,
                "isPeakTime": false,
                "players": [
                    {
                        "encodedContactId": "ABCDEFGHIJKLMNOP123456",
                        "fullName": "Nicholas Daskalovic",
                        "isLeadPlayer": true
                    }
               ],
                "sportsPackageId": 1
            },
            "duration": 60,
            "isPartOfACourse": null,
            "encodedBookingReference": "ABCDEFGHIJKLMNOP123456",
            "siteId": 2,
            "startTime": "14:00",
            "status": "held",
            "type": "court",
            "isChargeableIfRebooked": false,
            "canMemberCancel": true
        }
        '''
        payload = {
            "bookedMemberEncodedContactId": self._encodedContactId,
            "courtId": courtId,
            "date": date,
            "startTime": time,
            "sportsPackageId": 1,
            "playersEncodedContactIds": []
        }
        response = self._post(SINGLE_COURT_URL, payload)
        logger.info(
            f"[Check Court] Checked court {courtId}({courts_codes_reverse[courtId]}) on {date} at {time}")
        return response.json()

    def _get_recent_players(self) -> dict:
        '''
        Returns:
        {
            "recentPlayers": [
                {
                    "memberReferenceNumber": "123456",
                    "encodedContactId": "ABCDEFGHIJKLMNOP123456",
                    "fullName": "Steve Jobs",
                    "numberOfCourtsSharedWithMember": 4,
                    "paymentRequiredForCourtBookings": False,
                    "peakBookingsAllowed": True,
                    "homeClubSiteId": 2
                },
                ...
           ]
        }
        '''
        response = self._get(RECENT_PLAYERS_URL)
        logger.info("[Get Recent Players Court] Got recent players")
        return response.json()

    def _make_booking(self, encodedBookingRef: str) -> dict:
        '''
        Returns:
        {
            "bookedMemberEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookedByEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookingReference": "REF-C3C78DD-D5AD",
            "date": "2024-10-02",
            "details": {
                "courtId": 16704,
                "isPeakTime": false,
                "players": [
                    {
                        "encodedContactId": "ABCDEFGHIJKLMNOP123456",
                        "fullName": "Nicholas Daskalovic",
                        "isLeadPlayer": true
                    }
               ],
                "sportsPackageId": 1
            },
            "duration": 60,
            "isPartOfACourse": null,
            "encodedBookingReference": "ABCDEFGHIJKLMNOP123456",
            "siteId": 2,
            "startTime": "21:30",
            "status": "held",
            "type": "court",
            "isChargeableIfRebooked": false,
            "canMemberCancel": true
        }
        '''
        url = BOOKING_URL.format(encodedBookingRef=encodedBookingRef)
        payload = {
            "playersEncodedContactIds": [self._encodedContactId]
        }
        response = self._put(url, payload)
        logger.info("[Make Booking] Made Booking")
        return response.json()

    def _confirm_booking(self, encodedBookingRef: str) -> dict:
        '''
        Returns:
        {
            "bookedMemberEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookedByEncodedContactId": "ABCDEFGHIJKLMNOP123456",
            "bookingReference": "REF-C3C78DD-D5AD",
            "date": "2024-10-02",
            "details": {
                "courtId": 16704,
                "isPeakTime": false,
                "players": [
                    {
                        "encodedContactId": "ABCDEFGHIJKLMNOP123456",
                        "fullName": "Nicholas Daskalovic",
                        "isLeadPlayer": true
                    }
               ],
                "sportsPackageId": 1
            },
            "duration": 60,
            "isPartOfACourse": null,
            "encodedBookingReference": "ABCDEFGHIJKLMNOP123456",
            "siteId": 2,
            "startTime": "21:30",
            "status": "provisional",
            "type": "court",
            "isChargeableIfRebooked": false,
            "canMemberCancel": true
        }
        '''
        url = CONFIRM_URL.format(encodedBookingRef=encodedBookingRef)
        payload = {
            "courtConfirmationType": "provisional"
        }
        response = self._post(url, payload)
        logger.info("[Confirm Booking] Confirmed Booking")
        return response.json()

    def _post(self, url: str, payload: dict) -> requests.Response:
        response = requests.post(
            url, headers=self.headers, json=payload, impersonate="chrome")
        if response.status_code == 200:
            logger.debug(
                f"[POST] Received response 200 from {url}, payload={payload}")
            return response
        logger.error(
            f"[POST] Error when making POST request url={url}, payload={payload}, status={response.status_code}, response={response.content}")
        raise Exception(
            f"Error when making POST request:\nURL: {url}\nPayload: {payload}\nStatus: {response.status_code}\nResponse: {response.content}")

    def _put(self, url: str, payload: dict) -> requests.Response:
        response = requests.put(url, headers=self.headers,
                                json=payload, impersonate="chrome")
        if response.status_code == 200:
            logger.debug(
                f"[PUT] Received response 200 from {url}, payload={payload}")
            return response
        logger.error(
            f"[PUT] Error when making PUT request url={url}, payload={payload}, status={response.status_code}, response={response.content}")
        raise Exception(
            f"Error when making PUT request:\nURL: {url}\nPayload: {payload}\nStatus: {response.status_code}\nResponse: {response.content}")

    def _get(self, url: str) -> requests.Response:
        response = requests.get(
            url, headers=self.headers, impersonate="chrome")
        if response.status_code == 200:
            logger.debug(f"[GET] Received response 200 from {url}")
            return response
        logger.error(
            f"[GET] Error when making GET request url={url}, status={response.status_code}, response={response.content}")
        raise Exception(
            f"Error when making GET request:\nURL: {url}\nStatus: {response.status_code}\nResponse: {response.content}")

    def find_and_book_court(self, date: str, time: str) -> bool:
        logger.info(
            f"[Book Court] Attempting to book a court on {date} at {time}")
        all_available_courts = self._get_courts(date)
        if len(all_available_courts) == 0:
            logger.info(
                f"[Book Court] No courts found for {date} - probably soft blocked or already booked at this time")
            return False
        matching_courts = [
            court for court in all_available_courts if court['startTime'] == time]
        matching_hard_courts = [
            court for court in matching_courts if court['courtId'] in HARD_COURTS]
        matching_carpet_courts = [
            court for court in matching_courts if court['courtId'] in courts_codes_reverse.keys()]
        if len(matching_hard_courts) > 0:
            courtId = matching_hard_courts[0]['courtId']
        elif len(matching_carpet_courts) > 0:
            courtId = matching_carpet_courts[0]['courtId']
        else:
            logger.info(
                f"[Book Court] No indoor courts available on {date} at {time}")
            return False
        court_check = self._check_court(date, time, courtId)
        encodedBookingRef = court_check['encodedBookingReference']
        # Just to avoid strange request activity
        self._get_recent_players()
        self._make_booking(encodedBookingRef)
        self._confirm_booking(encodedBookingRef)
        logger.info(
            f"[Book Court] Booked court {courts_codes_reverse[courtId]} at {time} on {date}")
        return True
