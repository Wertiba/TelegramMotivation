import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow
from fastapi.responses import RedirectResponse
from test_auth import retrieve_user_by_state, SCOPES
from fastapi.responses import HTMLResponse
from tgbot import bot

app = FastAPI()
CREDS = {}
@app.get("/oauth2callback")
async def callback(request: Request):
    state = request.query_params.get('state')
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        state=state,
        redirect_uri='http://localhost:5000/oauth2callback'
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    telegram_user_id = retrieve_user_by_state(state)  # найти ID по state
    CREDS[telegram_user_id] = creds
    bot.send_message(telegram_user_id, 'Успешно')

    # Собираем ссылку deep link обратно в телеграм
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("domain_server:app", host="0.0.0.0", port=5000, reload=True)
