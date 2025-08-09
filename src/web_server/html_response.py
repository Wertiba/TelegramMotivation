def success_html():
    return """
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
    """

def homepage_html():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <meta name="description" content="Описание твоего сайта" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="your-custom-meta" content="custom value" />
        <title>Главная страница</title>
        <meta name="google-site-verification" content="OVhkLaeMtBGi_2cHiVH5_XjHlqfkFFM4G5fQqfYkNrY" />
    </head>
    <body>
        <h1>Добро пожаловать на главную страницу!</h1>
    </body>
    </html>
    """
