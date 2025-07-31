from datetime import datetime, time, timedelta
from src.services.singleton import singleton
import pytz


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


# tz = Timezone("Europe/Moscow")
# # Пример использования
# server_day_change = tz.get_user_day_change("UTC")
# print("Смена дня пользователя в серверной зоне:", server_day_change)
#
# server_time = tz.convert_user_time_to_server("UTC", "14:30")
# print("Введённое время пользователя в серверной зоне:", server_time)
