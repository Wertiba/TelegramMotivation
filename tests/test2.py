from src.logger import Logger

logger = Logger().get_logger()

logger.info('hello world')
logger.debug('hello world')
logger.error('hello world')
logger.warning('hello world')
logger.critical('hello world')
