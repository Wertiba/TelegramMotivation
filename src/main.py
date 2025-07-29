import threading

from src.bot import run_bot
from src.servicies.login_server.domain_server import run_uvicorn

if __name__ == "__main__":
    threading.Thread(target=run_uvicorn()).start()
    threading.Thread(target=run_bot()).start()
