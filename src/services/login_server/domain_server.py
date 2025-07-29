import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from google_auth_oauthlib.flow import Flow
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.bot import bot
from src.services.google_integration.settings import SCOPES, CREDS_PATH, REDIRECT_URI
from src.services.google_integration.o2auth import Authentication
from src.services.DB.storage import Storage

app = FastAPI()
auth = Authentication()
storage = Storage()

@app.get("/oauth2callback")
async def callback(request: Request):
    state = request.query_params.get('state')
    flow = Flow.from_client_secrets_file(
        CREDS_PATH,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    user_tgid = auth.retrieve_user_by_state(state)
    storage.save_creds(user_tgid, creds.to_json())
    bot.send_message(user_tgid, 'Успешно!')

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
    uvicorn.run("src.services.login_server.domain_server:app", host="0.0.0.0", port=5000, reload=True)

if __name__ == '__main__':
    run_uvicorn()
