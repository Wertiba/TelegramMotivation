import datetime
import pymysql
from loguru import logger
from contextlib import contextmanager
from src.services.DB.pool import get_pool

class Storage:
    def __init__(self, host, user, password, name, **conn_params):
        self.pool = get_pool(host, user, password, name, **conn_params)

    @contextmanager
    def connection(self):
        """Обычное соединение (автоматически закрывается)"""
        conn = self.pool.connection()
        try:
            yield conn
        except pymysql.MySQLError as e:
            logger.error("MySQL connection error: %s", e)
            raise
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """Транзакция с commit/rollback"""
        conn = self.pool.connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Transaction rolled back: %s", e)
            raise
        finally:
            conn.close()

    def execute(self, query, params=None):
        """Выполнение запроса без возврата результата"""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)

    def fetch_one(self, query, params=None):
        """Получить одну запись"""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def fetch_all(self, query, params=None):
        """Получить несколько записей"""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def set_timezone(self, timezone, tgid):
        self.execute("UPDATE users SET timezone = %s WHERE tgid = %s", params=(timezone, tgid))

    def get_timezone(self, tgid):
        return self.fetch_one("SELECT timezone FROM users WHERE tgid = %s", params=(tgid,))


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

    def get_tgid_by_state(self, state):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT tgid FROM users WHERE state = %s", (state,))
                return cur.fetchone()

    def set_state(self, tgid, state):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET state = %s WHERE tgid = %s", (state, tgid))

    def save_creds(self, tgid, creds):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET token = %s WHERE tgid = %s", (creds, tgid))

    def get_token(self, tgid):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT token FROM users WHERE tgid = %s", (tgid,))
                return cur.fetchone()

    def get_idusers(self, tgid):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT idusers FROM users WHERE tgid = %s", (tgid,))
                return cur.fetchone()
