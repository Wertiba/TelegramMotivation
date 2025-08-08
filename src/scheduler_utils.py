from apscheduler.schedulers.background import BackgroundScheduler

def create_scheduler():
    sched = BackgroundScheduler()
    return sched

def motivation_functional_wrapper(tgid):
    from src.bot import motivation_functional
    return motivation_functional(tgid)
