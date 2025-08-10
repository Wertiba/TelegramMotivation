import telebot
import json
import time
import requests
import os

from telebot.apihelper import ApiTelegramException
from dotenv import find_dotenv, load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from settings.config import SCOPES, SERVER_TIMEZONE, charset, port, MESSAGES_PATH
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

with open(MESSAGES_PATH, encoding='utf-8') as f:
    messages = json.load(f)


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not storage.is_user_already_registered(message.chat.id):
        storage.add_new_user(message.chat.id, message.from_user.first_name)

    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    token = storage.get_token(message.chat.id)

    if token and token[0]:
        bot.send_message(message.chat.id, messages[lang]["system_messages"]["start_register"])

    else:
        markup = auth_markup(message.chat.id, auth)
        bot.send_message(message.chat.id, messages[lang]["system_messages"]["start_unregister"], reply_markup=markup)


@bot.message_handler(commands=['motivation'])
def motivation_handler(message):
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    if not get_creds(message.chat.id):
        markup = auth_markup(message.chat.id, auth)
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["need_login"], reply_markup=markup)
        return

    msgid = bot.send_message(message.chat.id, messages[lang]["info_messages"]["processing_prompt"])
    motivation_functional(message.chat.id, msgid)


@bot.message_handler(commands=['about'])
def about_handler(message):
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    bot.send_message(message.chat.id, messages[lang]["system_messages"]["about"])


@bot.message_handler(commands=['settings'])
def settings_handler(message):
    markup = settings_markup(message.chat.id, auth)
    language = storage.get_language_by_tgid(message.chat.id)[0][0]
    # msg = f'Текущие настройки:\nЯзык: {language}\n'
    msg = messages[language]["info_messages"]["settings"]["msg1"] + language
    has_google = get_creds(message.chat.id)
    if has_google:
        timezone = storage.get_timezone(message.chat.id)[0]
        # msg += f'Таймзона: {timezone}\nПривязан google календарь'
        msg += messages[language]["info_messages"]["settings"]["msg2"] + timezone + messages[language]["info_messages"]["settings"]["msg3"]
    else:
        msg += messages[language]["info_messages"]["settings"]["msg4"]

    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(func=lambda m: True, content_types=[
    'text', 'audio', 'document', 'photo', 'sticker', 'video',
    'video_note', 'voice', 'location', 'contact', 'venue',
    'animation', 'dice', 'poll', 'game', 'invoice',
    'successful_payment', 'connected_website', 'passport_data', 'web_app_data'
])
def any_message(message):
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    bot.send_message(message.chat.id, messages[lang]["system_messages"]["any_text"])


@bot.message_handler()
def get_user_time(message, old_time, message_id):
    markup = settings_markup(message.chat.id, auth)
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    if message.content_type != 'text':
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["only_text"], reply_markup=markup)
        return

    user_tz = storage.get_timezone(message.chat.id)[0]
    bot.delete_message(message.chat.id, message_id)

    try:
        new_time = tz.convert_user_time_to_server(user_tz, tz.parse_time(message.text)).time()
    except Exception:
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["incorrect_time_format"], reply_markup=markup)
        return

    if not new_time:
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["incorrect_time_format"], reply_markup=markup)
        return
    if old_time:
        storage.delete_notification_by_id(old_time)
        scheduler.change_notification(message.chat.id, old_time, new_time)
    else:
        scheduler.add_notification(message.chat.id, new_time)
    bot.send_message(message.chat.id, messages[lang]["success_messages"]["notification_added"], reply_markup=markup)


@bot.message_handler()
def get_memory_prompt_from_user(message, message_id):
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    markup = settings_markup(message.chat.id, auth)
    if message.content_type != 'text':
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["only_text"], reply_markup=markup)
        return

    prompt = message.text
    storage.set_memory_prompt(prompt, message.chat.id)
    bot.delete_message(message.chat.id, message_id)
    bot.send_message(message.chat.id, messages[lang]["success_messages"]["prompt_added"], reply_markup=markup)


@bot.message_handler()
def get_user_time_for_tz(message, message_id):
    lang = storage.get_language_by_tgid(message.chat.id)[0][0]
    markup = change_timezone_markup(message.chat.id)
    if message.content_type != 'text':
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["only_text"], reply_markup=markup)
        return

    bot.delete_message(message.chat.id, message_id)

    try:
        new_time = tz.parse_time(message.text)
    except Exception:
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["incorrect_time_format"], reply_markup=markup)
        return

    if not new_time:
        bot.send_message(message.chat.id, messages[lang]["error_messages"]["incorrect_time_format"], reply_markup=markup)
        return
    else:
        user_tz = tz.guess_timezone_from_local_time(new_time)
        storage.set_timezone(user_tz, message.chat.id)
        bot.send_message(message.chat.id, messages[lang]["success_messages"]["change_timezone"] + user_tz)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = json.loads(call.data)
    tgid = call.message.chat.id
    level = data['level']
    lang = storage.get_language_by_tgid(tgid)[0][0]
    bot.clear_step_handler_by_chat_id(tgid)

    if level == 'calendar':
        if data['value'] == 'yandex':
            bot.answer_callback_query(
                callback_query_id=call.id,
                text=messages[lang]["system_messages"]["yandex_error"],
                show_alert=True
            )

        # elif data['value'] == 'google':

    elif level == 'settings':
        if data['value'] == 'notify_time':
            if not get_creds(tgid):
                markup = auth_markup(tgid, auth)
                bot.edit_message_text(messages[lang]["error_messages"]["need_login"], tgid, call.message.message_id, reply_markup=markup)
                return

            user_tz = storage.get_timezone(tgid)
            notifications = storage.get_all_notifications(tgid)
            markup = select_notification_time_markup(notifications, user_tz, lang)
            bot.edit_message_text(messages[lang]["info_messages"]["select_time"], tgid, call.message.message_id, reply_markup=markup)

        elif data['value'] == 'language':
            markup = select_language_markup()
            bot.edit_message_text(messages[lang]["info_messages"]["select_language"], tgid, call.message.message_id, reply_markup=markup)

        elif data['value'] == 'my_info':
            bot.edit_message_text(messages[lang]["info_messages"]["get_info_about_user"], tgid, call.message.message_id, reply_markup=None)
            bot.register_next_step_handler(call.message, get_memory_prompt_from_user, call.message.message_id)

    elif level == 'notify_time':
        markup = delete_notification_markup(data['value'], lang)
        bot.edit_message_text(messages[lang]["info_messages"]["get_new_notification_time"], tgid, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(call.message, get_user_time, data['value'], call.message.message_id)

    elif level == 'del_time':
        storage.delete_notification_by_id(data['value'])
        scheduler.remove_notification(data['value'])
        markup = settings_markup(tgid, auth)
        bot.edit_message_text(messages[lang]["success_messages"]["disable_notification"], tgid, call.message.message_id, reply_markup=markup)

    elif level == 'language':
        storage.set_language(data['value'], tgid)
        markup = settings_markup(tgid, auth)
        bot.edit_message_text(messages[data['value']]["success_messages"]["change_language"], tgid, call.message.message_id, reply_markup=markup)

    elif level == 'change_tz':
        bot.edit_message_text(messages[lang]["info_messages"]["get_new_time_for_timezone"], tgid, call.message.message_id, reply_markup=None)
        bot.register_next_step_handler(call.message, get_user_time_for_tz, call.message.message_id)

def motivation_functional(tgid, msgid=None):
    creds = get_creds(tgid)
    lang = storage.get_language_by_tgid(tgid)[0][0]
    if not creds:
        markup = retry_login_markup(tgid, auth)
        bot.send_message(tgid, messages[lang]["error_messages"]["re_entry"], reply_markup=markup)
        return

    events = calender.get_events(creds, tgid)
    prompt = str(events)
    idusers = storage.get_idusers(tgid)
    storage.save_request(idusers, 'user', prompt)
    motivation = gemma.process_prompt(idusers, prompt)
    bot.send_message(tgid[0], motivation, parse_mode='Markdown') if not msgid else bot.edit_message_text(motivation, tgid, msgid.message_id)


def get_creds(tgid):
    try:
        creds = None
        token = storage.get_token(tgid)

        if token and token[0]:
            creds = Credentials.from_authorized_user_info(json.loads(token[0]), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    storage.set_creds(tgid, creds.to_json())
                    return creds
                except RefreshError:
                    logger.warning(f"Google token expired for user {tgid}, need re-auth")
                    return False
            else:
                return False
        return creds
    except Exception as e:
        logger.error(f"Error while getting creds from user: {e}")
        return False

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
