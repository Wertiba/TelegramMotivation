import os

from dotenv import find_dotenv, load_dotenv
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.services.timezone import Timezone
from src.services.google_integration.settings import SERVER_TIMEZONE, MAX_EVENTS
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, port
from src.services.singleton import singleton
from src.logger import Logger


@singleton
class CalenderClient:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.tz = Timezone(SERVER_TIMEZONE)
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)
        self.logger = Logger().get_logger()

    def get_events(self, creds, tgid):
        try:
            service = build("calendar", "v3", credentials=creds)
            user_tz = self.storage.get_timezone(tgid)[0]

            start_of_day = self.tz.get_user_day_change(user_tz)
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            start_iso = start_of_day.isoformat()
            end_iso = end_of_day.isoformat()
            calendar_list = service.calendarList().list().execute()
            result = ''

            for calendar in calendar_list['items']:
                calendar_id = calendar['id']
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_iso,
                    timeMax=end_iso,
                    singleEvents=True,
                    orderBy="updated",
                    maxResults=MAX_EVENTS
                ).execute()
                events = events_result.get("items", [])

                if not events:
                    continue

                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    result += (start + ' ' + event['summary'])

            return result if result else 'нет никаких событий'

        except HttpError as error:
            self.logger.error(f"Error while getting calendar events: {error}")
