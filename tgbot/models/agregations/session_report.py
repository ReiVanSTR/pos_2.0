from ..basic import ObjectId
from typing import Union

def report_aggregation(session_id: Union[str, ObjectId]):
    if isinstance(session_id, str):
        session_id = ObjectId(session_id)

    aggregation = [
        {
            '$match': {
                '_id': session_id
            }
        }, {
            '$facet': {
                'session_data': [
                    {
                        '$lookup': {
                            'from': 'Users', 
                            'localField': 'opened_by', 
                            'foreignField': 'user_id', 
                            'as': 'opened_by'
                        }
                    }, {
                        '$lookup': {
                            'from': 'Users', 
                            'localField': 'closed_by', 
                            'foreignField': 'user_id', 
                            'as': 'closed_by'
                        }
                    }, {
                        '$project': {
                            '_id': '$_id', 
                            'opened_by': {
                                'user_data': {
                                    '$first': '$opened_by'
                                }, 
                                'timestamp': '$start_time'
                            }, 
                            'closed_by': {
                                'user_data': {
                                    '$first': '$closed_by'
                                }, 
                                'timestamp': '$end_time'
                            }, 
                            'session_time': {
                                '$dateDiff': {
                                    'startDate': '$start_time', 
                                    'endDate': '$end_time', 
                                    'unit': 'minute'
                                }
                            }
                        }
                    }
                ], 
                'employer_sellings': [
                    {
                        '$lookup': {
                            'from': 'bills', 
                            'localField': 'bills', 
                            'foreignField': '_id', 
                            'as': 'bills'
                        }
                    }, {
                        '$unwind': '$bills'
                    }, {
                        '$lookup': {
                            'from': 'orders', 
                            'localField': 'bills.orders', 
                            'foreignField': '_id', 
                            'as': 'bills.orders'
                        }
                    }, {
                        '$lookup': {
                            'from': 'Users', 
                            'localField': 'bills.created_by', 
                            'foreignField': 'user_id', 
                            'as': 'bills.created_by'
                        }
                    }, {
                        '$project': {
                            '_id': '$bills._id', 
                            'bill_data': '$bills', 
                            'bill_cost': {
                                '$sum': '$bills.orders.cost'
                            }, 
                            'orders_count': {
                                '$size': '$bills.orders'
                            }
                        }
                    }, {
                        '$group': {
                            '_id': {
                                '$first': '$bill_data.created_by.username'
                            }, 
                            'bills': {
                                '$push': {
                                    'bill_data': '$bill_data', 
                                    'bill_cost': '$bill_cost', 
                                    'orders_count': '$order_count'
                                }
                            }, 
                            'bills_by_card': {
                                '$push': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'card'
                                            ]
                                        }, 
                                        'then': {
                                            'bill_name': '$bill_data.bill_name', 
                                            'bill_cost': '$bill_cost', 
                                            'orders_count': '$orders_count'
                                        }, 
                                        'else': '$$REMOVE'
                                    }
                                }
                            }, 
                            'card_total': {
                                '$sum': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'card'
                                            ]
                                        }, 
                                        'then': '$bill_cost', 
                                        'else': 0
                                    }
                                }
                            }, 
                            'bills_by_cash': {
                                '$push': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'cash'
                                            ]
                                        }, 
                                        'then': {
                                            'bill_name': '$bill_data.bill_name', 
                                            'bill_cost': '$bill_cost', 
                                            'orders_count': '$orders_count'
                                        }, 
                                        'else': '$$REMOVE'
                                    }
                                }
                            }, 
                            'cash_total': {
                                '$sum': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'cash'
                                            ]
                                        }, 
                                        'then': '$bill_cost', 
                                        'else': 0
                                    }
                                }
                            }, 
                            'chief': {
                                '$push': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'chief'
                                            ]
                                        }, 
                                        'then': {
                                            'bill_name': '$bill_data.bill_name', 
                                            'bill_cost': '$bill_cost', 
                                            'orders_count': '$orders_count'
                                        }, 
                                        'else': '$$REMOVE'
                                    }
                                }
                            }, 
                            'chief_total': {
                                '$sum': {
                                    '$cond': {
                                        'if': {
                                            '$eq': [
                                                '$bill_data.payment_method', 'chief'
                                            ]
                                        }, 
                                        'then': '$bill_cost', 
                                        'else': 0
                                    }
                                }
                            }, 
                            'total_sellings': {
                                '$sum': {
                                    '$cond': {
                                        'if': {
                                            '$in': [
                                                '$bill_data.payment_method', [
                                                    'card', 'cash'
                                                ]
                                            ]
                                        }, 
                                        'then': '$orders_count', 
                                        'else': 0
                                    }
                                }
                            }, 
                            'total_orders': {
                                '$sum': '$orders_count'
                            }
                        }
                    }
                ], 
                'tabacco_data': [
                    {
                        '$lookup': {
                            'from': 'bills', 
                            'localField': 'bills', 
                            'foreignField': '_id', 
                            'as': 'bills'
                        }
                    }, {
                        '$unwind': '$bills'
                    }, {
                        '$lookup': {
                            'from': 'orders', 
                            'localField': 'bills.orders', 
                            'foreignField': '_id', 
                            'as': 'bills.orders'
                        }
                    }, {
                        '$unwind': '$bills.orders'
                    }, {
                        '$unwind': {
                            'path': '$bills.orders.cart', 
                            'preserveNullAndEmptyArrays': True
                        }
                    }, {
                        '$addFields': {
                            'cart_obj': {
                                '$objectToArray': '$bills.orders.cart'
                            }
                        }
                    }, {
                        '$unwind': '$cart_obj'
                    }, {
                        '$addFields': {
                            'cart_obj_id': {
                                '$toObjectId': '$cart_obj.k'
                            }, 
                            'cart_used_weight': '$cart_obj.v'
                        }
                    }, {
                        '$lookup': {
                            'from': 'tabacco', 
                            'localField': 'cart_obj_id', 
                            'foreignField': '_id', 
                            'as': 'data'
                        }
                    }, {
                        '$group': {
                            '_id': {
                                '$first': '$data.label'
                            }, 
                            'tabacco_data': {
                                '$push': {
                                    '_id': {
                                        '$first': '$data._id'
                                    }, 
                                    'label': {
                                        '$first': '$data.label'
                                    }, 
                                    'brand': {
                                        '$first': '$data.brand'
                                    }, 
                                    'used': '$cart_used_weight'
                                }
                            }, 
                            'total_used': {
                                '$sum': '$cart_used_weight'
                            }
                        }
                    }, {
                        '$sort': {
                            'total_used': -1
                        }
                    }
                ], 
                'work_hours': [
                    {
                        '$lookup': {
                            'from': 'shifts', 
                            'let': {
                                'session_start_time': '$start_time', 
                                'session_end_time': '$end_time'
                            }, 
                            'pipeline': [
                                {
                                    '$match': {
                                        '$expr': {
                                            '$and': [
                                                {
                                                    '$gte': [
                                                        '$start_time', '$$session_start_time'
                                                    ]
                                                }, {
                                                    '$lte': [
                                                        '$end_time', '$$session_end_time'
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }, {
                                    '$lookup': {
                                        'from': 'Users', 
                                        'localField': 'user_id', 
                                        'foreignField': 'user_id', 
                                        'as': 'user_data'
                                    }
                                }, {
                                    '$group': {
                                        '_id': {
                                            '$first': '$user_data.username'
                                        }, 
                                        'work_time': {
                                            '$push': '$$ROOT'
                                        }, 
                                        'total_hours': {
                                            '$sum': '$work_time.hours'
                                        }, 
                                        'total_minutes': {
                                            '$sum': '$work_time.minutes'
                                        }
                                    }
                                }
                            ], 
                            'as': 'matched_shifts'
                        }
                    }, {
                        '$project': {
                            '_id': False, 
                            'shifts': '$matched_shifts'
                        }
                    }
                ]
            }
        }, {
            '$project': {
                '_id': False, 
                'session_data': {
                    '$first': '$session_data'
                }, 
                'employers_selling': '$employer_sellings', 
                'total_selling_by_card': {
                    '$sum': '$employer_sellings.card_total'
                }, 
                'total_selling_cash': {
                    '$sum': '$employer_sellings.cash_total'
                }, 
                'total_selling_chief': {
                    '$sum': '$employer_sellings.chief_total'
                }, 
                'tabacco_data': '$tabacco_data', 
                'total_tabacco': {
                    '$sum': '$tabacco_data.total_used'
                }, 
                'work_hours': {
                    '$first': '$work_hours'
                }
            }
        }
    ]
    return aggregation