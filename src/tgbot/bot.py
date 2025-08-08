import telebot
import json
import time
import requests
import os

from telebot.apihelper import ApiTelegramException
from dotenv import find_dotenv, load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from settings.config import SCOPES, SERVER_TIMEZONE, charset, port
from settings.ollama_settings import model, url
from src.services.logger import Logger
from src.services.timezone import Timezone
from src.google_integration.o2auth import Authentication
from src.google_integration.calender_client import CalenderClient
from src.ollama.ollama_client import OllamaClient
from src.DB.storage import Storage
from src.scheduler.scheduler import MessageScheduler
from src.tgbot.keyboards import auth_markup, retry_login_markup, change_timezone_markup, settings_markup, select_language_markup, select_notification_time_markup, delete_notification_markup

load_dotenv(find_dotenv())

scheduler = MessageScheduler()
scheduler.start()
auth = Authentication()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)
logger = Logger().get_logger()
calender = CalenderClient()
gemma = OllamaClient(url, model)
tz = Timezone(SERVER_TIMEZONE)


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not storage.is_user_already_registered(message.chat.id):
        storage.add_new_user(message.chat.id, message.from_user.first_name)

    token = storage.get_token(message.chat.id)
    if token and token[0]:
        bot.send_message(message.chat.id, 'И снова здравствуйте!')

    else:
        markup = auth_markup(message.chat.id, auth)
        bot.send_message(message.chat.id, 'Приветствую! чтобы пользоваться ботом, надо привязать свой календарь', reply_markup=markup)


@bot.message_handler(commands=['motivation'])
def motivation_handler(message):
    if not get_creds(message.chat.id):
        markup = auth_markup(message.chat.id, auth)
        bot.send_message(message.chat.id, 'Для начала нужно привязать свой календарь!', reply_markup=markup)
        return
    motivation_functional(message.chat.id)


@bot.message_handler(commands=['about'])
def motivation_handler(message):
    bot.send_message(message.chat.id, 'это мы')


@bot.message_handler(commands=['settings'])
def motivation_handler(message):
    markup = settings_markup(message.chat.id, auth)
    language = storage.get_language_by_tgid(message.chat.id)[0][0]
    msg = f'Текущие настройки:\nЯзык: {language}\n'
    has_google = get_creds(message.chat.id)
    if has_google:
        timezone = storage.get_timezone(message.chat.id)[0]
        msg += f'Таймзона: {timezone}\nПривязан google календарь'
    else:
        msg += 'Календарь не привязан'

    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(func=lambda m: True,content_types=[
    'text', 'audio', 'document', 'photo', 'sticker', 'video',
    'video_note', 'voice', 'location', 'contact', 'venue',
    'animation', 'dice', 'poll', 'game', 'invoice',
    'successful_payment', 'connected_website', 'passport_data', 'web_app_data'
])
def any_message(message):
    bot.send_message(message.chat.id, 'Просто сообщение')


@bot.message_handler()
def get_user_time(message, old_time, message_id):
    markup = settings_markup(message.chat.id, auth)
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Пожалуйста, отправьте текст, а не фото/видео/документ.", reply_markup=markup)
        return

    user_tz = storage.get_timezone(message.chat.id)[0]
    new_time = tz.convert_user_time_to_server(user_tz, tz.parse_time(message.text)).time()
    bot.delete_message(message.chat.id, message_id)

    if not new_time:
        bot.send_message(message.chat.id, 'Неверный формат! Разрешенные форматы ввода: HH:MM, HH, Ip, HH.MM, HH:MM:SS', reply_markup=markup)
        return
    if old_time:
        storage.delete_notification_by_id(old_time)
        scheduler.change_notification(message.chat.id, old_time, new_time)
    else:
        scheduler.add_notification(message.chat.id, new_time)
    bot.send_message(message.chat.id, 'Уведомление добавлено!', reply_markup=markup)


@bot.message_handler()
def get_memory_prompt_from_user(message, message_id):
    markup = settings_markup(message.chat.id, auth)
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Пожалуйста, отправьте текст, а не фото/видео/документ.", reply_markup=markup)
        return

    prompt = message.text
    storage.set_memory_prompt(prompt, message.chat.id)
    bot.delete_message(message.chat.id, message_id)
    bot.send_message(message.chat.id, 'Промт добавлен!!', reply_markup=markup)


@bot.message_handler()
def get_user_time_for_tz(message, message_id):
    markup = change_timezone_markup()
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Пожалуйста, отправьте текст, а не фото/видео/документ.", reply_markup=markup)
        return

    bot.delete_message(message.chat.id, message_id)
    new_time = tz.parse_time(message.text)

    if not new_time:
        bot.send_message(message.chat.id, 'Неверный формат! Разрешенные форматы ввода: HH:MM, HH, Ip, HH.MM, HH:MM:SS', reply_markup=markup)
        return
    else:
        user_tz = tz.guess_timezone_from_local_time(new_time)
        storage.set_timezone(user_tz, message.chat.id)
        bot.send_message(message.chat.id, f'Временная зона изменена на {user_tz}!')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = json.loads(call.data)
    tgid = call.message.chat.id
    level = data['level']
    bot.clear_step_handler_by_chat_id(tgid)

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
            if not get_creds(tgid):
                markup = auth_markup(tgid, auth)
                bot.edit_message_text('Для начала нужно привязать свой календарь!', tgid, call.message.message_id, reply_markup=markup)
                return

            user_tz = storage.get_timezone(tgid)
            notifications = storage.get_all_notifications(tgid)
            markup = select_notification_time_markup(notifications, user_tz)
            bot.edit_message_text('Выберите время, которое хотите изменить', tgid, call.message.message_id, reply_markup=markup)

        elif data['value'] == 'language':
            markup = select_language_markup()
            bot.edit_message_text('Выберите ваш язык | Choose your language', tgid, call.message.message_id, reply_markup=markup)

        elif data['value'] == 'my_info':
            bot.edit_message_text('Хорошо, пришлите текст, в котором вы расскажете нейросети о себе, чтобы получать более персонализированные ответы', tgid, call.message.message_id, reply_markup=None)
            bot.register_next_step_handler(call.message, get_memory_prompt_from_user, call.message.message_id)

    elif level == 'notify_time':
        markup = delete_notification_markup(data['value'])
        bot.edit_message_text('Пожалуйста, введите новое время для уведомления', tgid, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(call.message, get_user_time, data['value'], call.message.message_id)

    elif level == 'del_time':
        storage.delete_notification_by_id(data['value'])
        scheduler.remove_notification(data['value'])
        markup = settings_markup(tgid, auth)
        bot.edit_message_text('Уведомление отключено', tgid, call.message.message_id, reply_markup=markup)

    elif level == 'language':
        markup = settings_markup(tgid, auth)
        storage.set_language(data['value'], tgid)
        bot.edit_message_text('Язык успешно изменён', tgid, call.message.message_id, reply_markup=markup)

    elif level == 'change_tz':
        bot.edit_message_text('Хорошо, тогда введите следующим сообщением ваше текущее время', tgid, call.message.message_id, reply_markup=None)
        bot.register_next_step_handler(call.message, get_user_time_for_tz, call.message.message_id)

def motivation_functional(tgid):
    creds = get_creds(tgid)
    if not creds:
        markup = retry_login_markup(tgid, auth)
        bot.send_message(tgid, 'Вам нужно войти заново, чтобы продолжить', reply_markup=markup)
        return

    events = calender.get_events(creds, tgid)
    prompt = str(events)
    idusers = storage.get_idusers(tgid)
    storage.save_request(idusers, 'user', prompt)
    motivation = gemma.process_prompt(idusers, prompt)
    bot.send_message(tgid, motivation, parse_mode='Markdown')


def get_creds(tgid):
    creds = None
    token = storage.get_token(tgid)

    if token and token[0]:
        creds = Credentials.from_authorized_user_info(json.loads(token[0]), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            storage.set_creds(tgid, creds.to_json())
            return creds
        else:
            return False
    return creds

def run_bot():
    scheduler.run_all_notifications()
    delay = 5  # начальная задержка
    max_delay = 300  # максимум 5 минут

    while True:
        try:
            logger.info("Bot is running")
            bot.polling(none_stop=True, interval=0, timeout=20)

            # сбрасываем задержку
            delay = 5

        except requests.exceptions.ReadTimeout:
            logger.debug("Read timeout – no new messages, continuing polling...")
            continue

        except ApiTelegramException as e:
            if e.error_code == 403 and 'bot was blocked by the user' in e.result:
                logger.debug(f"User blocked the bot - skipping")
            else:
                logger.error(f"Telegram API error: {e}")
            continue

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}. Restarting in {delay} sec...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # увеличиваем задержку

        except Exception as e:
            logger.exception(f"Unexpected error: {e}. Restarting in {delay} sec...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # увеличиваем задержку
