from datetime import datetime
import re

def parse_time(time_str):
    """
    Преобразует строку времени в datetime с округлением до минут.
    Поддерживаемые форматы:
      - "15:30", "14-20", "14.20.47", "8pm", "8:15 am"
    """

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

        return datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)

    # === Унификация формата с разделителями ===
    parts = re.split(r"[:.\-_ ]", time_str)  # Заменяем любые разделители
    parts = [int(p) for p in parts if p]     # Убираем пустые и приводим к числу

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

    return datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)


if __name__ == '__main__':
    while True:
        print(parse_time(str(input('введите время: '))))
