from tgbot.models.basic import ObjectId
from typing import Union
def get_total(session_id: Union[str, ObjectId]):
    
    if isinstance(session_id, str):
        session_id = ObjectId(session_id)

    pipeline = [
        {
            '$match':{
                '_id':session_id
            }
        },
        {
            '$unwind': '$bills'
        }, {
            '$lookup': {
                'from': 'bills', 
                'localField': 'bills', 
                'foreignField': '_id', 
                'as': 'bill_data'
            }
        }, {
            '$unwind': '$bill_data'
        }, {
            '$unwind': '$bill_data.orders'
        }, {
            '$lookup': {
                'from': 'orders', 
                'localField': 'bill_data.orders', 
                'foreignField': '_id', 
                'as': 'bill_order'
            }
        }, {
            '$group': {
                '_id': None, 
                'total_cost': {
                    '$sum': {
                        '$reduce': {
                            'input': '$bill_order.cost', 
                            'initialValue': 0, 
                            'in': {
                                '$add': [
                                    '$$value', '$$this'
                                ]
                            }
                        }
                    }
                }, 
                'total_order': {
                    '$sum': 1
                }
            }
        }
    ]

    return pipeline