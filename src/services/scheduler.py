import os
from loguru import logger
from src.logger import Logger
from dotenv import find_dotenv, load_dotenv
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, port
from src.services.singleton import singleton
from src.scheduler_utils import create_scheduler, motivation_functional_wrapper

@singleton
class MessageScheduler:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.scheduler = create_scheduler()
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)
        self.logger = Logger().get_logger()
        self.scheduler.add_listener(self.listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()

    def add_notification(self, tgid, event_time):
        """Добавление задач для конкретного пользователя"""

        if len(self.storage.get_all_notifications(tgid)) < 3:
            idnotifications = str(self.storage.add_notification(tgid, event_time))
            self.scheduler.add_job(
                motivation_functional_wrapper,
                "cron",
                hour=event_time.hour,
                minute=event_time.minute,
                args=[tgid],
                id=str(idnotifications),
                replace_existing=True
            )
            return True
        else:
            return False

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

    def get_jobs(self):
        """
        Возвращает список всех запланированных заданий.
        """
        return self.scheduler.get_jobs()

    def run_all_notifications(self):
        notifications = self.storage.get_notifications_from_all_users()

        for n in notifications:
            idnotifications, idusers, notify_time = n
            tgid = self.storage.get_tgid(idusers)
            total_seconds = int(notify_time.total_seconds())
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds % 3600) // 60

            self.scheduler.add_job(
                motivation_functional_wrapper,
                "cron",
                hour=hours,
                minute=minutes,
                args=[tgid],
                id=str(idnotifications),
                replace_existing=True
            )

    def listener(self, event):
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
