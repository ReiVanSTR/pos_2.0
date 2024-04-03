from datetime import datetime
from dataclasses import dataclass
from pydantic import Field
from typing import List
from .basic import ObjectId, Basic


@dataclass
class BillData():
    _id: ObjectId 
    bill_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    orders: List[ObjectId] #orders id
    is_closed: bool
    opened_by: List
    edited_by: List

class Bills(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    bill_name: str
    created_by: int #telegram user_id
    timestamp: datetime
    orders: List[ObjectId] #orders id
    is_closed: bool
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
        return BillData(**await cls._collection.find_one({"_id":ObjectId(bill_id)}))

    @classmethod
    async def update_orders(cls, bill_id: ObjectId, order_id):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)
        await cls._collection.update_one({"_id":bill_id}, {"$push":{"orders":order_id}}, upsert = True)

    @classmethod
    async def close_bill(cls, bill_id: ObjectId):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)

        await cls._collection.update_one({"_id":bill_id}, {"$set":{"is_closed":True}})

    

Bills.set_collection('bills')