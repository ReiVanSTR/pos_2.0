from tgbot.models.basic import ObjectId
from typing import Union
from datetime import datetime, timezone

def get_employer_sellings(user_id, from_date, to_date):
    pipeline = [
        {
            '$match': {
                'user_id': user_id, 
                'start_time': {
                    '$gte': datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, tzinfo=timezone.utc), 
                    '$lt': datetime(to_date.year, to_date.month, to_date.day, 0, 0, 0, tzinfo=timezone.utc)
                }
            }
            }, {
            '$group': {
                '_id': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$start_time'
                    }
                }, 
                'hours': {
                    '$sum': '$work_time.hours'
                }, 
                'minutes': {
                    '$sum': '$work_time.minutes'
                }, 
                'user_id': {
                    '$first': '$user_id'
                }, 
                'start_time': {
                    '$first': '$start_time'
                }, 
                'end_time': {
                    '$first': '$end_time'
                }
            }
        }, {
            '$lookup': {
                'from': 'orders', 
                'let': {
                    'start_time': '$start_time', 
                    'end_time': '$end_time', 
                    'user_id': '$user_id'
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {
                                        '$eq': [
                                            '$created_by', '$$user_id'
                                        ]
                                    }, {
                                        '$gte': [
                                            '$timestamp', '$$start_time'
                                        ]
                                    }, {
                                        '$lte': [
                                            '$timestamp', '$$end_time'
                                        ]
                                    }
                                ]
                            }
                        }
                    }, {
                        '$group': {
                            '_id': None, 
                            'sellings': {
                                '$sum': {
                                    '$cond': {
                                        'if': {
                                            '$and': [
                                                {
                                                    '$not': [
                                                        {
                                                            '$eq': [
                                                                '$cost', 0
                                                            ]
                                                        }
                                                    ]
                                                }, {
                                                    '$not': [
                                                        {
                                                            '$eq': [
                                                                '$cost', 40
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }, 
                                        'then': 1, 
                                        'else': 0
                                    }
                                }
                            }
                        }
                    }
                ], 
                'as': 'orders'
            }
        }, {
            '$lookup': {
                'from': 'Users', 
                'localField': 'user_id', 
                'foreignField': 'user_id', 
                'as': 'user_detail'
            }
        }, {
            '$group': {
                '_id': '$user_id', 
                'username': {
                    '$first': '$user_detail.username'
                }, 
                'total_hours': {
                    '$sum': '$hours'
                }, 
                'total_minutes': {
                    '$sum': '$minutes'
                }, 
                'shifts': {
                    '$push': {
                        'date': '$_id', 
                        'start_time': '$start_time', 
                        'end_time': '$end_time', 
                        'hours': '$hours', 
                        'minutes': '$minutes', 
                        'sellings': {
                            '$first': '$orders.sellings'
                        }
                    }
                }
            }
        }, {
            '$addFields': {
                'total_hours': {
                    '$add': [
                        '$total_hours', {
                            '$floor': {
                                '$divide': [
                                    '$total_minutes', 60
                                ]
                            }
                        }
                    ]
                }, 
                'total_minutes': {
                    '$mod': [
                        '$total_minutes', 60
                    ]
                }
            }
        }, {
            '$project': {
                '_id': 1, 
                'username': {
                    '$first': '$username'
                }, 
                'shifts': {
                    '$sortArray': {
                        'input': '$shifts', 
                        'sortBy': {
                            'date': 1
                        }
                    }
                }, 
                'total_hours': 1, 
                'total_minutes': 1, 
                'total_sellings': {
                    '$sum': '$shifts.sellings'
                }
            }
        }
    ]
    return pipeline