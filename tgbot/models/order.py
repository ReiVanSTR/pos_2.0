from datetime import datetime
from dataclasses import dataclass
from .basic import Basic, ObjectId 
from pydantic import Field
from typing import List

@dataclass
class HookahOrder:
    timestamp: datetime
    tabacco_cart: List

class Order(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    order_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    cart: List
    is_closed: bool =  Field(default = False)

    @classmethod
    async def create_order(cls, order_name, user_id):
        document = {
            "order_name": order_name,
            "created_by": user_id,
            "timestamp": datetime.utcnow(),
            "cart": []
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id

Order.set_collection('orders')