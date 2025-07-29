import telebot
import json
import time
import requests

from telebot import types

from src.logger import Logger
from src.config import token
from src.services.google_auth.o2auth import main, get_auth_url
from src.services.DB.storage import Storage


bot = telebot.TeleBot(token)
storage = Storage()
logger = Logger()

# @bot.message_handler(commands=['start'])
# def on_start(message):
#     args = message.text.split(maxsplit=1)
#     if len(args) == 2 and args[1].startswith("authed_"):
#         state = args[1][len("authed_"):]
#         telegram_id = message.from_user.id
#         if retrieve_user_by_state(state):
#             bot.send_message(telegram_id, "✅ Успешная авторизация!")
#         else:
#             bot.send_message(telegram_id, "❌ Не удалось подтвердить авторизацию.")
#     else:
#         bot.send_message(message.chat.id, "Привет! Используй /login")


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not storage.is_user_already_registered(message.chat.id):
        storage.add_new_user(message.chat.id, message.from_user.first_name)



    markup = types.InlineKeyboardMarkup()
    # btn_google_calendar = types.InlineKeyboardButton('Привязать google', callback_data=json.dumps({'level': 'calendar', 'value': 'google'}))
    btn_google_calendar = types.InlineKeyboardButton("Войти через Google", url=get_auth_url(message.from_user.id))
    btn_yandex_calendar = types.InlineKeyboardButton('Привязать yandex', callback_data=json.dumps({'level': 'calendar', 'value': 'yandex'}))
    markup.row(btn_google_calendar, btn_yandex_calendar)

    bot.send_message(message.chat.id, 'Приветствую!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_query(call):
    data = json.loads(call.data)
    level = data['level']

    if level == 'calendar':
        if data['value'] == 'yandex':
            bot.answer_callback_query(
                callback_query_id=call.id,
                text='Coming soon)',
                show_alert=True  # Это показывает всплывающее окно
            )

        elif data['value'] == 'google':
            events = main()
            bot.send_message(call.message.chat.id, str(events))


def run_bot():
    while True:
        try:
            logger.info("bot is running")
            bot.polling(none_stop=True)
        except requests.exceptions.ConnectionError:
            logger.error("bot isn't running: Connection error")
            time.sleep(5)
