import telebot
import json
import time
import requests
import os

from dotenv import load_dotenv, find_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.logger import Logger
from src.services.google_integration.o2auth import Authentication
from src.services.google_integration.calender_client import CalenderClient
from src.services.ollama.ollama_client import OllamaClient
from src.services.ollama.ollama_settings import model, url
from src.services.DB.storage import Storage
from src.services.google_integration.settings import SCOPES
from src.services.DB.database_config import charset, port
from src.keyboards import auth_markup, retry_login_markup, change_timezone, settings_markup, select_language_markup, select_notification_time_markup

load_dotenv(find_dotenv())

auth = Authentication()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), port, charset)
logger = Logger()
calender = CalenderClient()
gemma = OllamaClient(url, model)


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not storage.is_user_already_registered(message.chat.id):
        storage.add_new_user(message.chat.id, message.from_user.first_name)

    token = storage.get_token(message.chat.id)
    if token and token[0] and message.chat.id != int(os.getenv('MY_ID')):
        bot.send_message(message.chat.id, 'И снова здравствуйте!')

    else:
        markup = auth_markup(message.chat.id, auth)
        bot.send_message(message.chat.id, 'Приветствую! чтобы пользоваться ботом, надо привязать свой календарь', reply_markup=markup)


@bot.message_handler(commands=['motivation'])
def motivation_handler(message):
    motivation_functional(message.chat.id)

@bot.message_handler(commands=['about'])
def motivation_handler(message):
    bot.send_message(message.chat.id, 'это мы')

@bot.message_handler(commands=['settings'])
def motivation_handler(message):
    markup = settings_markup()
    bot.send_message(message.chat.id, 'текущие настройки:', reply_markup=markup)


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

    elif level == 'settings':
        if data['value'] == 'notify_time':
            user_tz = storage.get_timezone(call.message.chat.id)
            notifications = storage.get_all_notifications(call.message.chat.id)
            markup = select_notification_time_markup(notifications, user_tz)
            bot.send_message(call.message.chat.id, 'Выберите время, которое хотите изменить', reply_markup=markup)


def motivation_functional(tgid):
    creds = None
    token = storage.get_token(tgid)

    if token and token[0]:
        creds = Credentials.from_authorized_user_info(json.loads(token[0]), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            storage.save_creds(tgid, creds.to_json())
        else:
            markup = retry_login_markup(tgid, auth)
            bot.send_message(tgid, 'пожалуйста, войдите заново', reply_markup=markup)
            return

    events = calender.get_events(creds, tgid)
    prompt = str(events)
    idusers = storage.get_idusers(tgid)
    storage.save_request(idusers, 'user', prompt)
    motivation = gemma.process_prompt(idusers, prompt)
    bot.send_message(tgid, motivation, parse_mode='Markdown')


def run_bot():
    delay = 5  # начальная задержка
    max_delay = 300  # максимум 5 минут

    while True:
        try:
            logger.info("Bot is running")
            bot.polling(none_stop=True, interval=0, timeout=20)

            # сбрасываем задержку
            delay = 5
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}. Restarting in {delay} sec...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # увеличиваем задержку
        except Exception as e:
            logger.exception(f"Unexpected error: {e}. Restarting in {delay} sec...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # увеличиваем задержку
