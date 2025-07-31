import asyncio
import threading
import os
from dotenv import find_dotenv, load_dotenv
from src.services.DB.pool import DatabaseConnection
from src.bot import run_bot
from src.services.login_server.domain_server import run_uvicorn
from src.services.DB.database_config import charset

def start():
    DatabaseConnection.init_pool(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db_name=os.getenv('DB_NAME'),
        charset=charset
    )

    threading.Thread(target=run_bot, daemon=True).start()
    run_uvicorn()

if __name__ == "__main__":
    start()
