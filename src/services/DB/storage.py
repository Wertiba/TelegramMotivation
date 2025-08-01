import datetime
import pymysql
from loguru import logger
from contextlib import contextmanager
from src.services.singleton import singleton
from dbutils.pooled_db import PooledDB


@singleton
class Storage:
    def __init__(self, host, user, password, database, charset, port=3306, creator=pymysql, mincached=1, maxcached=5, maxconnections=10, blocking=True, ping=1):
        db_config = {
            "creator": creator,
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "charset": charset,

            "mincached": mincached,
            "maxcached": maxcached,
            "maxconnections": maxconnections,
            "blocking": blocking,
            "ping": ping
        }
        self._pool = PooledDB(**db_config)

    @contextmanager
    def connection(self):
        """Обычное соединение (автоматически закрывается)"""
        conn = self._pool.connection()
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
        conn = self._pool.connection()
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
        with self.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.lastrowid

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
        self.execute("INSERT INTO users (tgid, name) VALUES (%s, %s);", params=(tgid, name))

    def save_request(self, idusers, role, content, created_at=datetime.datetime.now()):
        self.execute("""
                    INSERT INTO requests_history (idusers, role, content, created_at) VALUES (%s, %s, %s, %s);
                """, params=(idusers, role, content, created_at))

    def save_notification(self, tgid, time):
        return self.execute("INSERT INTO notifications (idusers, notify_time) VALUES ((SELECT idusers FROM users WHERE tgid = %s), %s);", params=(tgid, time))

    def is_user_already_registered(self, tgid):
        return bool(self.fetch_one("SELECT idusers FROM users WHERE tgid = %s", params=(tgid,)))

    def get_user_history(self, idusers, limit=30):
        return self.fetch_all("SELECT role, content FROM requests_history WHERE idusers = %s ORDER BY created_at ASC LIMIT %s", params=(idusers, limit))

    def get_tgid_by_state(self, state):
        return self.fetch_one("SELECT tgid FROM users WHERE state = %s", params=(state,))

    def set_state(self, tgid, state):
        self.execute("UPDATE users SET state = %s WHERE tgid = %s", params=(state, tgid))

    def save_creds(self, tgid, creds):
        self.execute("UPDATE users SET token = %s WHERE tgid = %s", params=(creds, tgid))

    def get_token(self, tgid):
        return self.fetch_one("SELECT token FROM users WHERE tgid = %s", params=(tgid,))

    def get_idusers(self, tgid):
        return self.fetch_one("SELECT idusers FROM users WHERE tgid = %s", params=(tgid,))

    def get_all_notifications(self, tgid):
        return self.fetch_all("SELECT idnotifications, notify_time FROM notifications WHERE idusers = (SELECT idusers FROM users WHERE tgid = %s)", params=(tgid,))

    def delete_notification_by_id(self, idnotifications):
        self.execute("DELETE FROM notifications WHERE idnotifications = %s", params=(idnotifications,))

    def delete_notification_by_time(self, tgid, time):
        self.execute("DELETE FROM notifications WHERE tgid = %s AND botify_time = %s", params=(tgid, time))

    def set_language(self, language, tgid):
        self.execute("UPDATE users SET language = %s WHERE tgid = %s", params=(language, tgid))
