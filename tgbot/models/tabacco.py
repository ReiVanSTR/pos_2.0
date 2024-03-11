from pydantic import Field
from typing import Union
from dataclasses import dataclass
from .basic import Basic, ObjectId

@dataclass
class TabaccoData():
    _id: ObjectId
    label: str
    brand: str
    type: str
    weight: float

    def to_dict(self):
        return {
            "_id":self._id.__str__(), 
            "label":self.label,
            "brand":self.brand,
            "type":self.type,
            "weight":self.weight
        }

class Tabacco(Basic):
    # id: int = Field(default_factory = int, alias = "_id")
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    label: str
    brand: str
    type: str
    weight: float = Field(default = 0)

    @classmethod
    async def get_by_id(cls, id: Union[ObjectId, str]):
        if isinstance(id, str):
            id = ObjectId(id)
        obj = await cls._collection.find_one({'_id': id})
        return TabaccoData(**obj) if obj else None
    
    @classmethod
    async def get_by_label(cls, label: str):
        obj = await cls._collection.find({"label":label})
        return TabaccoData(**obj) if obj else None
    
    @classmethod
    async def get_all_brands(cls):
        documents = cls._collection.find()
        return [document["brand"] async for document in documents]
    
    @classmethod
    async def get_all(cls):
        documents = cls._collection.find()
        return [TabaccoData(**document) async for document in documents]
    
    @classmethod
    async def get_all_brands_by_type(cls, type: str):
        documents = cls._collection.find({"type":type})
        result = []
        async for document in documents:
            result.append(document["brand"])

        return list(set(result))

    @classmethod
    async def get_by_brand(cls, brand: str):
        documents = cls._collection.find({"brand":brand})
        return [TabaccoData(**document) async for document in documents]
    
    @classmethod
    async def update_weight(cls, id: Union[ObjectId, str], new_weight):
        if isinstance(id, str):
            id = ObjectId(id)
        
        await cls._collection.update_one({"_id":id}, {"$set":{"weight":new_weight}})
    

Tabacco.set_collection('tabacco')