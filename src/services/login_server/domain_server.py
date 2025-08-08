import datetime
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from dotenv import load_dotenv, find_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.bot import bot, scheduler
from src.services.google_integration.settings import SCOPES, CREDS_PATH, REDIRECT_URI, SERVER_TIMEZONE
from src.services.google_integration.o2auth import Authentication
from src.services.DB.storage import Storage
from src.services.DB.database_config import charset, port
from src.services.timezone import Timezone
from src.bot_config import MORNING_TIME, EVENING_TIME, TIME_FROMAT
from src.keyboards import change_timezone_markup
from src.logger import Logger

load_dotenv(find_dotenv())

app = FastAPI()
auth = Authentication()
tz = Timezone(SERVER_TIMEZONE)
storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)
logger = Logger().get_logger()

@app.get("/oauth2callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    error = request.query_params.get('error')

    if error:
        logger.warning(f"Auth error: {error}")
        return HTMLResponse(f"Ошибка авторизации: {error}", status_code=400)


    if not code:
        logger.warning(f"Code parameter missing")
        return HTMLResponse("Отсутствует параметр code в ответе от Google", status_code=400)

    #не обрабатывается catch
    state = request.query_params.get('state')
    flow = Flow.from_client_secrets_file(
        CREDS_PATH,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    try:
        flow.fetch_token(authorization_response=str(request.url))
    except Exception as e:
        logger.error(f"Auth error: {error}")
        return HTMLResponse(f"Ошибка авторизации: {str(e)}", status_code=400)

    creds = flow.credentials
    user_tgid = auth.retrieve_user_by_state(state)
    if not user_tgid:
        logger.warning(f"Auth error: state is not valid")
        return HTMLResponse("Не совпадает параметр state. Скорее всего, вы хотите взломать сервер", status_code=401)

    storage.set_creds(user_tgid, creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    timezone_result = service.settings().get(setting="timezone").execute()
    timezone = timezone_result.get("value")
    storage.set_timezone(str(timezone), user_tgid)
    user_time = tz.convert_user_time_to_server(SERVER_TIMEZONE, datetime.datetime.now().strftime(TIME_FROMAT)).time().strftime(TIME_FROMAT)

    if len(storage.get_all_notifications(user_tgid)) == 0:
        morning_time = tz.convert_user_time_to_server(timezone, MORNING_TIME).time()
        evening_time = tz.convert_user_time_to_server(timezone, EVENING_TIME).time()
        scheduler.add_notification(user_tgid, morning_time)
        scheduler.add_notification(user_tgid, evening_time)

        bot.send_message(user_tgid,
                         f'Авторизация прошла успешно! Бот будет присылать уведомления с мотивацией в {MORNING_TIME} и {EVENING_TIME}. Изменить это время можно в /settings. Бот определил ваше время как {user_time}, если он сильно ошибся, то вам нужно изменить его!', reply_markup=change_timezone_markup())
    else:
        bot.send_message(user_tgid, f'Авторизация прошла успешно! Бот определил ваше время как {user_time}, если он сильно ошибся, то вам нужно изменить его!', reply_markup=change_timezone_markup())

    # return RedirectResponse(f"https://t.me/BestMotivationBot?start=authed_{state}")
    return HTMLResponse(content="""
        <html>
            <head>
                <title>Успешная авторизация</title>
                <style>
                    body { font-family: Arial; background: #f7f7f7; text-align: center; padding: 100px; }
                    .box { background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
                    h1 { color: green; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h1>✅ Успешная авторизация</h1>
                    <p>Теперь вы можете вернуться в Telegram.</p>
                    <a href="https://t.me/BestMotivationBot">Нажмите здесь, чтобы вернуться в бота</a>
                </div>
            </body>
        </html>
    """, status_code=200)

def run_uvicorn():
    import uvicorn
    uvicorn.run("src.services.login_server.domain_server:app", host="0.0.0.0", port=80, reload=False)

# if __name__ == '__main__':
#     run_uvicorn()
