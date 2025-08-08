import logging

from fastapi import FastAPI
from src.web_server.enpoints import router
from src.services.logger import Logger, InterceptHandler


logger = Logger().get_logger()
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(name).handlers = [InterceptHandler()]
    logging.getLogger(name).propagate = False

app = FastAPI()
app.include_router(router)

def run_uvicorn():
    import uvicorn
    uvicorn.run("src.web_server.app:app", host="0.0.0.0", port=80, reload=False, log_config=None)
