import telebot
import config  # подключаем конфиг, чтобы взять с него токен бота

bot = telebot.TeleBot(config.token)
print(bot.get_me())