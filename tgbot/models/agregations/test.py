from datetime import datetime, timezone
from tgbot.models.basic import ObjectId
from typing import Union
main = [
    {
        '$match': {
            'timestamp': {
                '$gte': datetime(2024, 5, 26, 22, 0, 0, tzinfo=timezone.utc), 
                '$lt': datetime(2024, 5, 27, 21, 59, 59, tzinfo=timezone.utc)
            }
        }
    }, {
        '$unwind': {
            'path': '$cart', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'cart_obj': {
                '$objectToArray': '$cart'
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
            '_id': '$_id', 
            'order_name': {
                '$first': '$order_name'
            }, 
            'created_by': {
                '$first': '$created_by'
            }, 
            'timestamp': {
                '$first': '$timestamp'
            }, 
            'cart': {
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
            'cost': {
                '$first': '$cost'
            }
        }
    }
]

def bill_pipeline(bill_id: Union[str, ObjectId]):
    if isinstance(bill_id, str):
        bill_id = ObjectId(bill_id)

    pipeline = [
        {
            '$match': {
                '_id':bill_id,
                'is_closed':True
            }
        }, {
            '$unwind': {
                'path': '$orders', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$lookup': {
                'from': 'orders', 
                'localField': 'orders', 
                'foreignField': '_id', 
                'as': 'order_data'
            }
        }, {
            '$unwind': {
                'path': '$order_data', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$lookup': {
                'from': 'Users', 
                'localField': 'created_by', 
                'foreignField': 'user_id', 
                'as': 'order_created_by'
            }
        }, {
            '$unwind': {
                'path': '$order_data.cart', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$addFields': {
                'cart_obj': {
                    '$objectToArray': '$order_data.cart'
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
            '$lookup': {
                'from': 'Users', 
                'localField': 'created_by', 
                'foreignField': 'user_id', 
                'as': 'created_by'
            }
        }, {
            '$group': {
                '_id': '$_id', 
                'bill_name': {
                    '$first': '$bill_name'
                }, 
                'created_by': {
                    '$first': '$created_by'
                }, 
                'timestamp': {
                    '$first': '$timestamp'
                }, 
                'orders': {
                    '$push': {
                        '_id': '$order_data._id', 
                        'order_name': '$order_data.order_name', 
                        'created_by': {
                            '$first': '$order_created_by'
                        }, 
                        'timestamp': '$order_data.timestamp', 
                        'cart': {
                            'tabacco_data': {
                                '$first': '$data'
                            }, 
                            'tabacco_used_weight': '$cart_used_weight'
                        }
                    }
                }, 
                'is_closed': {
                    '$first': '$is_closed'
                }, 
                'opened_by': {
                    '$first': '$opened_by'
                }, 
                'edited_by': {
                    '$first': '$edited_by'
                }, 
                'payment_method': {
                    '$first': '$payment_method'
                }
            }
        }
    ]
    return pipeline