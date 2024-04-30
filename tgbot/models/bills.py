from datetime import datetime
from dataclasses import dataclass
from pydantic import Field
from typing import List, Union
from .basic import ObjectId, Basic
import logging


@dataclass
class BillData():
    _id: ObjectId 
    bill_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    orders: List[ObjectId] #orders id
    is_closed: bool
    payment_method: str
    opened_by: List
    edited_by: List

class Bills(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    bill_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    orders: List[ObjectId] #orders id
    is_closed: bool
    payment_method: str
    opened_by: List
    edited_by: List

    @classmethod
    async def create_bill(cls, bill_name, user_id):
        document = {
            "bill_name": bill_name,
            "created_by": user_id,
            "timestamp": datetime.utcnow(),
            "orders": [],
            "is_closed": False,
            "payment_method":"cash",
            "opened_by": [],
            "edited_by": []
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
    @classmethod
    async def count_documents(cls, filtr = {}):
        response = await cls._collection.count_documents(filtr)
        return response

    @classmethod
    async def get_all_bills(cls, filtr = {}):
        documents = cls._collection.find(filtr)

        return [BillData(**document) async for document in documents]
    
    @classmethod
    async def get_bill(cls, bill_id: str):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)
        return BillData(**await cls._collection.find_one({"_id":bill_id}))

    @classmethod
    async def update_orders(cls, bill_id: ObjectId, order_id):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)
        await cls._collection.update_one({"_id":bill_id}, {"$push":{"orders":order_id}}, upsert = True)

    @classmethod
    async def remove_order(cls, bill_id: Union[ObjectId, str], order_id: Union[ObjectId, str]):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)

        if isinstance(order_id, str):
            order_id = ObjectId(order_id)

        await cls._collection.update_one({"_id":bill_id}, {"$pull":{"orders":order_id}}, upsert = True)

    @classmethod
    async def close_bill(cls, bill_id: ObjectId, payment_method: str):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)

        await cls._collection.update_one({"_id":bill_id}, {"$set":{"is_closed":True, "payment_method":payment_method}})

    @classmethod
    async def delete_bill(self, bill_id: ObjectId):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)

        result = await self._collection.delete_one({"_id":bill_id})
        logging.log(30, result)
    

Bills.set_collection('bills')