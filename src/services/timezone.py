from datetime import datetime, time, timedelta
from src.services.singleton import singleton
from src.bot_config import TIME_FROMAT
import pytz
import re


@singleton
class Timezone:
    def __init__(self, server_tz):
        self.server_tz = server_tz


    def get_user_day_change(self, user_tz_name: str) -> datetime:
        """
        Возвращает момент времени, когда у пользователя наступит новый день,
        но в таймзоне сервера.
        """
        server_tz = pytz.timezone(self.server_tz)
        user_tz = pytz.timezone(user_tz_name)

        now_server = datetime.now(server_tz)
        today_user = now_server.astimezone(user_tz).date()

        # 00:00 в таймзоне пользователя
        user_midnight = user_tz.localize(datetime.combine(today_user, time.min))
        server_midnight = user_midnight.astimezone(server_tz)

        # Если уже наступила полуночь пользователя — берём следующую
        if server_midnight <= now_server:
            next_midnight_user = user_midnight + timedelta(days=1)
            server_midnight = next_midnight_user.astimezone(server_tz)

        return server_midnight

    def convert_user_time_to_server(self, input_tz_name, input_time_str, output_timezone=False):
        """
        Конвертирует введённое пользователем время в таймзону сервера,
        используя текущую дату пользователя.
        """
        output_tz = pytz.timezone(self.server_tz) if not output_timezone else pytz.timezone(output_timezone)
        input_tz = pytz.timezone(input_tz_name)

        # Получаем сегодняшнюю дату в таймзоне пользователя
        today_user = datetime.now(input_tz).date()

        hours, minutes = map(int, input_time_str.split(':'))

        # Создаём datetime в зоне пользователя
        result_datetime = input_tz.localize(datetime.combine(today_user, time(hours, minutes)))

        # Конвертируем в серверную зону
        return result_datetime.astimezone(output_tz)


    def parse_time(self, time_str):
        """
        Преобразует строку времени в datetime с округлением до минут.
        Поддерживаемые форматы:
          - "15:30", "14-20", "14.20.47", "8pm", "8:15 am"
        """
        try:
            time_str = time_str.strip().lower()
            if not time_str:
                return False

            # === Обработка формата с AM/PM ===
            ampm_match = re.fullmatch(r"(\d{1,2})(?::(\d{1,2}))?\s*(am|pm)", time_str)
            if ampm_match:
                hours = int(ampm_match[1])
                minutes = int(ampm_match[2] or 0)
                period = ampm_match[3]

                if not (1 <= hours <= 12 and 0 <= minutes <= 59):
                    return False

                # Преобразуем 12-часовой формат в 24-часовой
                if period == "pm" and hours != 12:
                    hours += 12
                if period == "am" and hours == 12:
                    hours = 0

                return datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0).strftime(TIME_FROMAT)

            # === Унификация формата с разделителями ===
            parts = re.split(r"[:.\-_ ]", time_str)  # Заменяем любые разделители
            parts = [int(p) for p in parts if p]  # Убираем пустые и приводим к числу

            if not (1 <= len(parts) <= 3):
                return False

            # Заполняем недостающие значения нулями (часы, минуты, секунды)
            hours, minutes, seconds = (parts + [0, 0])[:3]

            # Проверяем диапазоны
            if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                return False

            # Округление секунд до минут
            if seconds >= 30:
                minutes += 1
                if minutes == 60:
                    hours, minutes = (hours + 1) % 24, 0

            return datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0).strftime(TIME_FROMAT)

        except Exception as e:
            return False
