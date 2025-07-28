import sys
from loguru import logger

class Logger:
    def __init__(self, write_stdout: bool = True):
        logger.remove()  # удаляем дефолтные обработчики

        if write_stdout:
            logger.add(
                sink=sys.stdout,
                colorize=True,
                format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
                level="INFO",
                enqueue=True
            )

        logger.add(
            sink="debug.txt",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="1 MB",
            compression="zip",
            enqueue=True
        )

        self._logger = logger

    def info(self, message: str):
        self._logger.info(message)

    def debug(self, message: str):
        self._logger.debug(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def exception(self, message: str):
        self._logger.exception(message)

    def get_logger(self):
        return self._logger  # если хочешь использовать напрямую loguru
