import time
import telebot
import json
import random

from storage import Storage
from loguru import logger
from telebot import types
from config import token, host, user, password, db_name
from test_auth import main


bot = telebot.TeleBot(token)
storage = Storage(host, user, password, db_name)

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup()
    btn_google_calendar = types.InlineKeyboardButton('Привязать google', callback_data=json.dumps({'level': 'calendar', 'value': 'google'}))
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

logger.info('Bot is running')
bot.polling(none_stop=True)
