import time
import telebot
import json
import random

from loguru import logger
from telebot import types
from config import token, host, user, password, db_name
from src.servicies.o2auth import main, get_auth_url, retrieve_user_by_state
from src.servicies.DB.storage import Storage


bot = telebot.TeleBot(token)
storage = Storage(host, user, password, db_name)

@bot.message_handler(commands=['start'])
def on_start(message):
    args = message.text.split(maxsplit=1)
    if len(args) == 2 and args[1].startswith("authed_"):
        state = args[1][len("authed_"):]
        telegram_id = message.from_user.id
        if retrieve_user_by_state(state):
            bot.send_message(telegram_id, "✅ Успешная авторизация!")
        else:
            bot.send_message(telegram_id, "❌ Не удалось подтвердить авторизацию.")
    else:
        bot.send_message(message.chat.id, "Привет! Используй /login")


@bot.message_handler()
def start_handler(message):
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

if __name__ == '__main__':
    logger.info('Bot is running')
    bot.polling(none_stop=True)
