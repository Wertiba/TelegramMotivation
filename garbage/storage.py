import pymysql

from contextlib import contextmanager
from loguru import logger

class Storage:
    def __init__(self, host, user, password, db_name):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': db_name,
            'autocommit': True
        }

    @contextmanager
    def connection(self):
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            yield conn
        except pymysql.MySQLError as e:
            logger.error("MySQL error while connection: %s", e)
            raise
        finally:
            if conn:
                conn.close()

    def add_new_user(self, ):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users ()
                    VALUES ()
                """, ())

    def is_user_already_registered(self):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT idplayers FROM players WHERE id = %s", (id,))
                return bool(cur.fetchone())
