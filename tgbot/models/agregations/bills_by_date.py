from datetime import datetime, timedelta, timezone

def get_bills_by_date(input_date: str):
    """
    :param input_date: date example = '2024-01-01'
    """
    date_object = datetime.strptime(input_date, "%Y-%m-%d").date()
    next_day = date_object + timedelta(days=1)

    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': datetime(date_object.year, date_object.month, date_object.day, 6, 5, 0, tzinfo=timezone.utc), 
                    '$lt': datetime(next_day.year, next_day.month, next_day.day, 6, 0, 0, tzinfo=timezone.utc)
                }
            }
        }, {
            '$group': {
                '_id': None, 
                'bills': {
                    '$push': '$_id'
                }
            }
        }, {
            '$project': {
                '_id': 0, 
                'bills': 1
            }
        }
    ]

    return pipeline