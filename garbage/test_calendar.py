from datetime import datetime, timedelta
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    try:
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(e)
        raise


# Получаем сервис
service = get_calendar_service()

# Определяем начало и конец сегодняшнего дня (по часовому поясу)
timezone = 'Europe/Moscow'  # ⚠️ Укажи свой! Например: 'America/New_York', 'Asia/Tokyo'

# Начало дня (00:00:00)
start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# Конец дня (23:59:59)
end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

# Преобразуем в ISO-формат с указанием временной зоны
start_iso = start_of_day.isoformat() + '+03:00'  # +03:00 — для Moscow. Или используй pytz
end_iso = end_of_day.isoformat() + '+03:00'

print(f"Ищу события с {start_iso} по {end_iso}")

# Запрос к API
events_result = service.events().list(
    calendarId='primary',
    timeMin=start_iso,
    timeMax=end_iso,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

if not events:
    print("На сегодня событий нет.")
else:
    print(f"Найдено {len(events)} событий на сегодня:")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'Без названия')
        print(f" — {start.split('T')[1][:5]}: {summary}")  # Время в формате ЧЧ:ММ
