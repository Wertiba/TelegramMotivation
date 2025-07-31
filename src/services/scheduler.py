import os
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, autocommit
from src.bot import motivation_functional


class MessageScheduler:
    def __init__(self):
        load_dotenv(find_dotenv())
        # self.bot = bot
        self.scheduler = BackgroundScheduler()
        self.storage = Storage(
            os.getenv('DB_HOST'),
            os.getenv('DB_USER'),
            os.getenv('DB_PASSWORD'),
            os.getenv('DB_NAME'),
            autocommit,
            charset
        )

    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()

    def add_notification(self, tgid, event_time, suffix):
        """Добавление задач для конкретного пользователя"""

        self.scheduler.add_job(
            motivation_functional,
            "cron",
            hour=event_time.hour,
            minute=event_time.minute,
            args=[tgid],
            id=f"user_{tgid}_{suffix}",
            replace_existing=True
        )

    def remove_notification(self, tgid, suffix):
        """Удаление задач пользователя по его ID"""
        job_id = f"user_{tgid}_{suffix}"
        job = self.scheduler.get_job(job_id)
        if job:
            self.scheduler.remove_job(job_id)

    def reschedule_user(self, user):
        """Обновление расписания для пользователя"""
        # self.remove_notification(user["id"])
        # self.add_notification(user)

    def load_all_users(self):
        """Загрузка задач для всех пользователей при старте"""
        # users = self.storage.get_all_users()  # метод должен вернуть список пользователей
        # for user in users:
        #     self.add_user_jobs(user)
