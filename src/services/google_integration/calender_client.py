from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.services.google_integration.settings import SCOPES

def auth_window():
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=8080, success_message='Hello world')
    print('test: a')
    return creds

def get_events(creds):
    try:
        service = build("calendar", "v3", credentials=creds)

        # Начало дня (00:00:00)
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Конец дня (23:59:59)
        end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
        # Преобразуем в ISO-формат с указанием временной зоны
        start_iso = start_of_day.isoformat() + '+03:00'  # +03:00 — для Moscow. Или используй pytz
        end_iso = end_of_day.isoformat() + '+03:00'

        print(f"Ищу события с {start_iso} по {end_iso}\n\n")

        # Запрос к API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_iso,
            timeMax=end_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
  creds = auth_window()
  events = get_events(creds)
  return events
