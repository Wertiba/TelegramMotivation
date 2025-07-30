from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.services.google_integration.settings import SCOPES


class CalenderClient:
    def __init__(self):
        pass

    def get_events(self, creds):
        try:
            service = build("calendar", "v3", credentials=creds)

            timezone_result = service.settings().get(setting="timezone").execute()
            timezone = timezone_result.get("value")

            # Начало дня (00:00:00)
            start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Конец дня (23:59:59)
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            # Преобразуем в ISO-формат с указанием временной зоны
            start_iso = start_of_day.isoformat() + '+03:00'  # +03:00 — для Moscow. Или используй pytz
            end_iso = end_of_day.isoformat() + '+03:00'

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
