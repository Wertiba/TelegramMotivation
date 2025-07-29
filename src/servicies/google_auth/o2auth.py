import os.path
import uuid

from google_auth_oauthlib.flow import Flow
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

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

def get_auth_url(telegram_user_id):
    state = str(uuid.uuid4())
    with open(fr'C:\Users\Wertiba\PycharmProjects\TelegramMotivation\garbage\{state}.txt', 'w') as f:
        f.write(str(telegram_user_id))

    flow = Flow.from_client_secrets_file(
        r"C:\Users\Wertiba\PycharmProjects\TelegramMotivation\src\servicies\google_auth\credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:5000/oauth2callback"
    )
    auth_url, _ = flow.authorization_url(state=state, access_type='offline', include_granted_scopes='true')
    return auth_url

def retrieve_user_by_state(state):
    with open(fr'C:\Users\Wertiba\PycharmProjects\TelegramMotivation\garbage\{state}.txt', 'r') as f:
        return int(f.read())

if __name__ == "__main__":
    main()
