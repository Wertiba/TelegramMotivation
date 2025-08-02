import json
import datetime

from telebot import types
from src.services.timezone import Timezone
from src.services.google_integration.settings import SERVER_TIMEZONE
from src.bot_config import MAX_COUNT_NOTIFICATIONS, TIME_FROMAT

def auth_markup(tgid, auth):
    markup = types.InlineKeyboardMarkup()
    yandex_data = json.dumps({'level': 'calendar', 'value': 'yandex'})
    btn_google_calendar = types.InlineKeyboardButton("Привязать google", url=auth.get_auth_url(tgid))
    btn_yandex_calendar = types.InlineKeyboardButton('Привязать yandex', callback_data=yandex_data)
    markup.row(btn_google_calendar, btn_yandex_calendar)
    return markup

def retry_login_markup(tgid, auth):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("повторить вход", url=auth.get_auth_url(tgid))
    markup.row(btn)
    return markup

def change_timezone_markup():
    markup = types.InlineKeyboardMarkup()
    data = json.dumps({'level': 'change_tz'})
    btn = types.InlineKeyboardButton("ввести своё время", callback_data=data)
    markup.row(btn)
    return markup

def settings_markup():
    markup = types.InlineKeyboardMarkup()
    change_language_data = json.dumps({'level': 'settings', 'value': 'language'})
    change_notify_time_data = json.dumps({'level': 'settings', 'value': 'notify_time'})
    change_user_info_data = json.dumps({'level': 'settings', 'value': 'my_info'})
    btn_change_language = types.InlineKeyboardButton("Изменить язык", callback_data=change_language_data)
    btn_change_notify_time = types.InlineKeyboardButton('Изменить время мотивационных сообщений', callback_data=change_notify_time_data)
    btn_change_user_info = types.InlineKeyboardButton('Изменить информацию о себе', callback_data=change_user_info_data)
    markup.row(btn_change_language)
    markup.row(btn_change_notify_time)
    markup.row(btn_change_user_info)
    return markup

def select_language_markup():
    markup = types.InlineKeyboardMarkup()
    ru_data = json.dumps({'level': 'language', 'value': 'ru'})
    en_data = json.dumps({'level': 'language', 'value': 'en'})
    btn_ru = types.InlineKeyboardButton("Русский ", callback_data=ru_data)
    btn_en = types.InlineKeyboardButton('English', callback_data=en_data)
    markup.row(btn_ru, btn_en)
    return markup

def select_notification_time_markup(notifications, user_tz):
    markup = types.InlineKeyboardMarkup()
    tz = Timezone(SERVER_TIMEZONE)

    for i in notifications:
        idnotifications, time = i
        total_seconds = int(time.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        formated_time = f"{hours:02d}:{minutes:02d}"
        user_time = tz.convert_user_time_to_server(SERVER_TIMEZONE, formated_time, user_tz[0])
        data = json.dumps({'level': 'notify_time', 'value': str(idnotifications)})
        btn = types.InlineKeyboardButton(user_time.time().strftime(TIME_FROMAT), callback_data=data)
        markup.row(btn)

    if len(notifications) < MAX_COUNT_NOTIFICATIONS:
        for i in range(len(notifications), MAX_COUNT_NOTIFICATIONS):
            data = json.dumps({'level': 'notify_time', 'value': None})
            btn = types.InlineKeyboardButton('Добавить время', callback_data=data)
            markup.row(btn)

    return markup

def delete_notification_markup(time):
    markup = None
    if time:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton('Удалить напоминание',
                                            callback_data=json.dumps({'level': 'del_time', 'value': time})))
    return markup

def add_time_button(time, current):
    data = json.dumps({'level': 'edit_time', 'input': time, 'output': current.strftime(TIME_FROMAT)})
    button = types.InlineKeyboardButton(current.strftime(TIME_FROMAT), callback_data=data)
    return button
