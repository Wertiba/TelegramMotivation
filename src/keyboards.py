import json

from telebot import types

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

def change_timezone():
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
    markup.row(btn_change_language, btn_change_notify_time)
    markup.row(btn_change_user_info)
    return markup

def select_language_markup():
    markup = types.InlineKeyboardMarkup()
    ru_data = json.dumps({'level': 'language', 'value': 'ru'})
    en_data = json.dumps({'level': 'language', 'value': 'en'})
    btn_ru = types.InlineKeyboardButton("Русский🇷🇺 ", callback_data=ru_data)
    btn_en = types.InlineKeyboardButton('English🇬🇧', callback_data=en_data)
    markup.row(btn_ru, btn_en)
    return markup
