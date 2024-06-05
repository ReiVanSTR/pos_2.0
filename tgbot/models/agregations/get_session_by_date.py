from datetime import datetime, timedelta, timezone


def get_pipeline(date):
    next_day = date + timedelta(days = 1)
    pipeline = [
        {
            '$match': {
                'start_time': {
                    '$gte': datetime(date.year, date.month, date.day, 6, 1, 0, tzinfo=timezone.utc), 
                    '$lt': datetime(next_day.year, next_day.month, next_day.day, 6, 0, 0, tzinfo=timezone.utc)
                }
            }
        }
    ]

    return pipeline