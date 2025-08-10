from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def guess_timezone_from_local_time(local_time_str: str) -> timezone:
    now_utc = datetime.now(timezone.utc)

    # Время в виде datetime (без tz)
    local_time = datetime.combine(now_utc.date(), datetime.strptime(local_time_str, '%H:%M').time(), tzinfo=timezone.utc)

    # Если локальное время сильно отстаёт или опережает — корректируем день
    if local_time > now_utc + timedelta(hours=12):
        local_time -= timedelta(days=1)
    elif local_time < now_utc - timedelta(hours=12):
        local_time += timedelta(days=1)

    # Разница
    offset = local_time - now_utc

    # Переводим в часы с округлением
    offset_hours = round(offset.total_seconds() / 3600)

    # Создаём объект timezone
    tz = timezone(timedelta(hours=offset_hours))
    return tz

def tz_to_str(tz: timezone) -> str:
    hours = tz.utcoffset(None).total_seconds() / 3600
    sign = '+' if hours >= 0 else '-'
    return f"UTC{sign}{abs(int(hours))}"

def get_utc_offset_from_name(tz_name: str) -> str:
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    offset = tz.utcoffset(now)

    hours = int(offset.total_seconds() // 3600)
    minutes = int((offset.total_seconds() % 3600) // 60)

    sign = '+' if hours >= 0 else '-'
    return f"UTC{sign}{abs(hours):02d}:{abs(minutes):02d}"

# Пример использования
print(get_utc_offset_from_name("Europe/Moscow"))
# Пример использования:
tz = guess_timezone_from_local_time('0:45')
print(f"Объект timezone: {tz}")
print(f"Текстовая зона: {tz_to_str(tz)}")
