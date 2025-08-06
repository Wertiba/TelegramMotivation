import sys
from loguru import logger
from pathlib import Path
from src.bot_config import LOGS_PATH
from src.services.singleton import singleton


@singleton
class Logger:
    def __init__(
        self,
        log_file: str = LOGS_PATH,
        log_level: str = "DEBUG",
        write_stdout: bool = True,
        rotation: str = "10 MB",
        retention: str = "7 days",
        compression: str = "zip",
    ):
        logger.remove()

        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        if write_stdout:
            logger.add(
                sink=sys.stdout,
                colorize=True,
                format=log_format,
                level=log_level,
                enqueue=True,
            )

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=log_path,
            format=log_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=True,
        )

        self._logger = logger

    def get_logger(self):
        """Возвращает готовый экземпляр loguru.logger"""
        return self._logger
