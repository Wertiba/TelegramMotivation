import pymysql
import datetime

from contextlib import contextmanager
from loguru import logger

from src.servicies.DB.database_config import host, user, password, db_name


class Storage:
    def __init__(self):
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

    def add_new_user(self, tgid, name):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (tgid, name) VALUES (%s, %s);
                """, (tgid, name))

    def save_request(self, idusers, role, content, created_at=datetime.datetime.now()):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO requests_history (idusers, role, content, created_at) VALUES (%s, %s, %s, %s);
                """, (idusers, role, content, created_at))

    def is_user_already_registered(self, tgid):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT idusers FROM users WHERE tgid = %s", (tgid,))
                return bool(cur.fetchone())

    def get_user_history(self, idusers):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT role, content FROM requests_history WHERE idusers = %s", (idusers,))
                return cur.fetchall()
