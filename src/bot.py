import telebot
import json
import time
import requests

from telebot import types
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.logger import Logger
from src.bot_config import token
from src.services.google_integration.o2auth import Authentication
from src.services.google_integration.calender_client import CalenderClient
from src.services.ollama.ollama_client import OllamaClient
from src.services.ollama.ollama_settings import model, url
from src.services.DB.storage import Storage
from src.services.google_integration.settings import SCOPES
from tests.test2 import de_emojify

auth = Authentication()
bot = telebot.TeleBot(token)
storage = Storage()
logger = Logger()
calender = CalenderClient()
gemma = OllamaClient(url, model)


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not storage.is_user_already_registered(message.chat.id):
        storage.add_new_user(message.chat.id, message.from_user.first_name)

    markup = types.InlineKeyboardMarkup()
    # btn_google_calendar = types.InlineKeyboardButton('Привязать google', callback_data=json.dumps({'level': 'calendar', 'value': 'google'}))
    btn_google_calendar = types.InlineKeyboardButton("Войти через Google", url=auth.get_auth_url(message.chat.id))
    btn_yandex_calendar = types.InlineKeyboardButton('Привязать yandex', callback_data=json.dumps({'level': 'calendar', 'value': 'yandex'}))
    markup.row(btn_google_calendar, btn_yandex_calendar)

    bot.send_message(message.chat.id, 'Приветствую!', reply_markup=markup)


@bot.message_handler(commands=['motivation'])
def motivation_handler(message):
    creds = None
    token = json.loads(storage.get_token(message.chat.id)[0])

    if token:
        creds = Credentials.from_authorized_user_info(token, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            storage.save_creds(message.chat.id, creds.to_json())
        else:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("повторить вход", url=auth.get_auth_url(message.chat.id))
            markup.row(btn)
            bot.send_message(message.chat.id, 'пожалуйста, войдите заново', reply_markup=markup)
            return

    events = calender.get_events(creds)
    idusers = storage.get_idusers(message.chat.id)
    prompt = f'мне нужна мотивация, сегодня меня ждут такие события: {events}'
    storage.save_request(idusers, 'user', de_emojify(prompt))
    motivation = gemma.process_prompt(idusers, prompt)
    bot.send_message(message.chat.id, motivation)

@bot.callback_query_handler(func=lambda callback: True)
def callback_query(call):
    data = json.loads(call.data)
    level = data['level']

    if level == 'calendar':
        if data['value'] == 'yandex':
            bot.answer_callback_query(
                callback_query_id=call.id,
                text='Coming soon)',
                show_alert=True
            )

        elif data['value'] == 'google':
            pass


def run_bot():
    while True:
        try:
            logger.info("bot is running")
            bot.polling(none_stop=True)
        except requests.exceptions.ConnectionError:
            logger.error("bot isn't running: Connection error")
            time.sleep(5)
