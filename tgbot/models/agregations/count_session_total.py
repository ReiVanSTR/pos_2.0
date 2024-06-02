pipeline = [
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