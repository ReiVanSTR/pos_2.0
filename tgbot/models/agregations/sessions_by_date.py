from datetime import datetime, timezone

def get_pipeline(from_date, to_date):
    pipeline = [
        {
            '$match': {
                'start_time': {
                    '$gte': datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, tzinfo=timezone.utc), 
                    '$lt': datetime(to_date.year, to_date.month, to_date.day, 0, 0, 0, tzinfo=timezone.utc)
                }
            }
        }, {
        '$project': {
            '_id': 0,
            'user': '$opened_by',
            'id': {
                '$toString': '$_id'
            }, 
            'date': {
                '$dateToString': {
                    'date': '$start_time', 
                    'format': '%m-%d-%Y'
                }
            }
        }
    }
]
    return pipeline