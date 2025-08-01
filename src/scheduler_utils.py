from apscheduler.schedulers.background import BackgroundScheduler

def create_scheduler():
    sched = BackgroundScheduler()
    return sched

def motivation_functional_wrapper(tgid):
    # здесь просто обёртка, которая внутри вызывает src.bot.motivation_functional
    from src.bot import motivation_functional
    return motivation_functional(tgid)
