import json
import os

from dotenv import load_dotenv, find_dotenv
from telebot import types
from settings.config import SERVER_TIMEZONE, MAX_COUNT_NOTIFICATIONS, TIME_FROMAT, MESSAGES_PATH, charset, port
from src.services.timezone import Timezone
from src.DB.storage import Storage


load_dotenv(find_dotenv())
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)
with open(MESSAGES_PATH, encoding='utf-8') as f:
    messages = json.load(f)


def auth_markup(tgid, auth):
    lang = storage.get_language_by_tgid(tgid)[0][0]
    markup = types.InlineKeyboardMarkup()
    yandex_data = json.dumps({'level': 'calendar', 'value': 'yandex'})
    btn_google_calendar = types.InlineKeyboardButton(messages[lang]["buttons"]["google_button"], url=auth.get_auth_url(tgid))
    btn_yandex_calendar = types.InlineKeyboardButton(messages[lang]["buttons"]["yandex_button"], callback_data=yandex_data)
    markup.row(btn_google_calendar, btn_yandex_calendar)
    return markup

def retry_login_markup(tgid, auth):
    lang = storage.get_language_by_tgid(tgid)[0][0]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(messages[lang]["buttons"]["retry_login"], url=auth.get_auth_url(tgid))
    markup.row(btn)
    return markup

def change_timezone_markup(tgid):
    lang = storage.get_language_by_tgid(tgid)[0][0]
    markup = types.InlineKeyboardMarkup()
    data = json.dumps({'level': 'change_tz'})
    btn = types.InlineKeyboardButton(messages[lang]["buttons"]["get_new_time_for_timezone"], callback_data=data)
    markup.row(btn)
    return markup

def settings_markup(tgid, auth):
    lang = storage.get_language_by_tgid(tgid)[0][0]
    markup = types.InlineKeyboardMarkup()
    change_language_data = json.dumps({'level': 'settings', 'value': 'language'})
    change_notify_time_data = json.dumps({'level': 'settings', 'value': 'notify_time'})
    change_user_info_data = json.dumps({'level': 'settings', 'value': 'my_info'})
    btn_change_language = types.InlineKeyboardButton(messages[lang]["buttons"]["change_language"], callback_data=change_language_data)
    btn_change_notify_time = types.InlineKeyboardButton(messages[lang]["buttons"]["reset_notify_time"], callback_data=change_notify_time_data)
    btn_change_user_info = types.InlineKeyboardButton(messages[lang]["buttons"]["change_info_about_user"], callback_data=change_user_info_data)
    btn_change_calendar = types.InlineKeyboardButton(messages[lang]["buttons"]["reset_calendar"], url=auth.get_auth_url(tgid))
    markup.row(btn_change_language)
    markup.row(btn_change_notify_time)
    markup.row(btn_change_user_info)
    markup.row(btn_change_calendar)
    return markup

def select_language_markup():
    markup = types.InlineKeyboardMarkup()
    ru_data = json.dumps({'level': 'language', 'value': 'ru'})
    en_data = json.dumps({'level': 'language', 'value': 'en'})
    btn_ru = types.InlineKeyboardButton(messages["ru"]["buttons"]["ru"], callback_data=ru_data)
    btn_en = types.InlineKeyboardButton(messages["ru"]["buttons"]["en"], callback_data=en_data)
    markup.row(btn_ru, btn_en)
    return markup

def select_notification_time_markup(notifications, user_tz, lang):
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
            btn = types.InlineKeyboardButton(messages[lang]["buttons"]["add_new_time"], callback_data=data)
            markup.row(btn)

    return markup

def delete_notification_markup(time, lang):
    markup = None
    if time:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(messages[lang]["buttons"]["delete_notification"], callback_data=json.dumps({'level': 'del_time', 'value': time})))
    return markup
