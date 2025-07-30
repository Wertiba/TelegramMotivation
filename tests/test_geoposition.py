import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Добавляем нужные права
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(r"C:\Users\Wertiba\PycharmProjects\TelegramMotivation\src\services\google_integration\credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

    try:
        service = build("calendar", "v3", credentials=creds)

        # 1️⃣ Получаем часовой пояс пользователя
        timezone_result = service.settings().get(setting="timezone").execute()
        timezone = timezone_result.get("value")
        print(f"User timezone: {timezone}")

        # 2️⃣ Получаем ближайшие 10 событий
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
