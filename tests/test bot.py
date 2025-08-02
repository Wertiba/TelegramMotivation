import telebot
import os
from telebot.types import LabeledPrice
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Команда старта
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я могу принять оплату Звёздами.\nНапиши /buy чтобы купить услугу.")

# Обработка покупки
@bot.message_handler(commands=['buy'])
def buy(message):
    prices = [LabeledPrice(label="Подписка Premium", amount=1000)]  # 1000 звёзд
    bot.send_invoice(
        message.chat.id,
        "Premium подписка",
        "Оплата Premium доступа в боте",
        "premium_payload",  # payload теперь 4-й аргумент
        "",  # provider_token
        "XTR",  # currency
        prices,
        start_parameter="premium-subscription"
    )

# Проверка платежа
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Успешный платеж
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "Спасибо за оплату! Premium активирован 🎉")

bot.infinity_polling()
