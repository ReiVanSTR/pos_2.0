from datetime import datetime
from dataclasses import dataclass
from .basic import Basic, ObjectId 
from pydantic import Field
from typing import List, Dict

@dataclass
class OrderData:
    _id: ObjectId 
    order_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    cart: List[Dict[str, int]]
    cost: int
    is_closed: bool = Field(default = False)

class Order(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    order_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    cart: List[Dict[str, int]]
    cost: int
    is_closed: bool =  Field(default = False)

    @classmethod
    async def create_order(cls, order_name, user_id, cart, cost):
        document = {
            "order_name": order_name,
            "created_by": user_id,
            "timestamp": datetime.utcnow(),
            "cart": cart,
            "cost": cost
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
    @classmethod
    async def get_order(cls, order_id):
        return OrderData(**await cls._collection.find_one({"_id":order_id}))
    

Order.set_collection('orders')