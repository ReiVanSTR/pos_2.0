from pydantic import Field
from typing import List, Dict
from datetime import datetime

from .basic import Basic, ObjectId

class EditingOrder(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    order_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    cart: List[Dict[str, int]]
    cost: int
    is_closed: bool =  Field(default = False)

    @classmethod
    async def create_order(cls, order_name, user_id, cart, cost, timestamp = None):
        document = {
            "order_name": order_name,
            "created_by": user_id,
            "timestamp": timestamp if timestamp else datetime.utcnow(),
            "cart": cart,
            "cost": cost
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
EditingOrder.set_collection("orders")