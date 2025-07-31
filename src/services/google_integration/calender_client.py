import os

from dotenv import find_dotenv, load_dotenv
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.services.timezone import Timezone
from src.services.google_integration.settings import SERVER_TIMEZONE
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, autocommit


class CalenderClient:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.tz = Timezone(SERVER_TIMEZONE)
        self.storage = Storage()

    def get_events(self, creds, tgid):
        try:
            service = build("calendar", "v3", credentials=creds)
            user_tz = self.storage.get_timezone(tgid)[0]

            start_of_day = self.tz.get_user_day_change(user_tz)
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            start_iso = start_of_day.isoformat()
            end_iso = end_of_day.isoformat()

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get("items", [])
            result = ''

            if not events:
                return 'нет никаких событий'

            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])
                result += (start + ' ' + event['summary'])

            return result

        except HttpError as error:
            print(f"An error occurred: {error}")
