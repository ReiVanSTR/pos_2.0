from datetime import datetime
from dataclasses import dataclass
from .basic import Basic, ObjectId 
from pydantic import Field
from bson import Timestamp
from typing import List, Union

@dataclass
class Changes():
    _id: int 
    timestamp: datetime
    user_id: int
    expected_weight: int
    accepted_weight: int

class Invent(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    tabacco_id: ObjectId
    changes: List

    @classmethod
    async def is_exists(cls, tabacco_id: ObjectId):
        
        result = await cls._collection.find_one({"tabacco_id":tabacco_id})
        return True if result else False

    @classmethod
    async def create(cls, tabacco_id):
        if await cls.is_exists(tabacco_id):
            return 
        
        document = {
            "tabacco_id":ObjectId(tabacco_id),
            "changes":[]
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
    @classmethod
    async def update_changes(cls, tabacco_id, changes: Changes):
        if not await cls.is_exists(tabacco_id):
            await cls.create(tabacco_id)

        pipeline = [
            {"$match":{"tabacco_id":tabacco_id}},
            {"$project":{"changes_size":{"$size":"$changes"}}}
        ]

        async for result in cls._collection.aggregate(pipeline):
            changes._id = result["changes_size"]

        await cls._collection.update_one({"tabacco_id":tabacco_id}, {"$push":{"changes":changes.__dict__}}, upsert = True)

Invent.set_collection('inventarization')