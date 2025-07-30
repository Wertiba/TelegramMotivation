from datetime import datetime, time, timedelta
import pytz


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


    def convert_user_time_to_server(self, user_tz_name: str, user_date: datetime.date,
                                    user_time_str: str) -> datetime:
        """
        Конвертирует введённое пользователем время (строкой) в таймзону сервера.

        :param user_tz_name: Название таймзоны пользователя (например, "Europe/Moscow")
        :param user_date: Дата (datetime.date) в зоне пользователя
        :param user_time_str: Время (например, "14:30")
        :return: datetime в таймзоне сервера
        """
        server_tz = pytz.timezone(self.server_tz)
        user_tz = pytz.timezone(user_tz_name)

        hours, minutes = map(int, user_time_str.split(':'))

        # создаём datetime в зоне пользователя
        user_datetime = user_tz.localize(datetime.combine(user_date, time(hours, minutes)))
        # конвертируем в серверную зону
        return user_datetime.astimezone(server_tz)


# tz = Timezone("Europe/Moscow")
# # Пример использования
# server_day_change = tz.get_user_day_change("UTC")
# print("Смена дня пользователя в серверной зоне:", server_day_change)
#
# user_date = datetime.now().date()
# server_time = tz.convert_user_time_to_server("UTC", user_date, "14:30")
# print("Введённое время пользователя в серверной зоне:", server_time)
