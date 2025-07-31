import os
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import find_dotenv, load_dotenv
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, port
from src.bot import motivation_functional
from src.services.singleton import singleton


@singleton
class MessageScheduler:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.scheduler = BackgroundScheduler()
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), port, charset)

    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()

    def add_notification(self, tgid, event_time):
        """Добавление задач для конкретного пользователя"""

        idnotifications = str(self.storage.save_notification(tgid, event_time))
        self.scheduler.add_job(
            motivation_functional,
            "cron",
            hour=event_time.hour,
            minute=event_time.minute,
            args=[tgid],
            id=idnotifications,
            replace_existing=True
        )

    def remove_notification(self, idnotifications):
        """Удаление задач пользователя по его ID"""
        job = self.scheduler.get_job(idnotifications)
        if job:
            self.scheduler.remove_job(idnotifications)
        else:
            logger.debug('Задача не найдена')

    def change_notification(self, tgid, idnotifications, new_time):
        """Обновление расписания для пользователя"""
        self.remove_notification(idnotifications)
        self.add_notification(tgid, new_time)

    def load_all_users(self):
        """Загрузка задач для всех пользователей при старте"""
        # users = self.storage.get_all_users()  # метод должен вернуть список пользователей
        # for user in users:
        #     self.add_user_jobs(user)
