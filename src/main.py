import threading
from src.bot import run_bot
from src.services.login_server.domain_server import run_uvicorn
from src.services.scheduler import MessageScheduler

if __name__ == "__main__":
    sheduler = MessageScheduler()
    sheduler.start()
    threading.Thread(target=run_bot, daemon=True).start()
    run_uvicorn()
