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
