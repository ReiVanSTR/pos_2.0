from datetime import datetime

def get_timedelta(time: datetime) -> str:
    return (str((datetime.now() - time)).split(', ')[-1]).split('.')[0]

