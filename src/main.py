import threading

from src.tgbot.bot import run_bot
from src.login_server.domain_server import run_uvicorn

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_uvicorn()
