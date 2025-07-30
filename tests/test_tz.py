from datetime import datetime, time, timedelta
import pytz


def get_user_day_change(server_tz_name: str, user_tz_name: str) -> datetime:
    """
    Возвращает момент времени, когда у пользователя наступит новый день,
    но в таймзоне сервера.

    :param server_tz_name: Название таймзоны сервера (например, "UTC")
    :param user_tz_name: Название таймзоны пользователя (например, "Europe/Moscow")
    :return: datetime в таймзоне сервера
    """
    server_tz = pytz.timezone(server_tz_name)
    user_tz = pytz.timezone(user_tz_name)

    now_server = datetime.now(server_tz)  # текущее время сервера
    today_user = now_server.astimezone(user_tz).date()  # текущая дата пользователя

    # 00:00 в таймзоне пользователя
    user_midnight = user_tz.localize(datetime.combine(today_user, time.min))
    server_midnight = user_midnight.astimezone(server_tz)

    # Если уже наступила полуночь пользователя — берём следующую
    if server_midnight <= now_server:
        next_midnight_user = user_midnight + timedelta(days=1)
        server_midnight = next_midnight_user.astimezone(server_tz)

    return server_midnight


# Пример использования:
server_day_change = get_user_day_change("Europe/Moscow", "UTC")
print("Смена дня пользователя в серверной зоне:", server_day_change)
