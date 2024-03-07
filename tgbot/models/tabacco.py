from pydantic import Field
from dataclasses import dataclass
from .basic import Basic, ObjectId

@dataclass
class TabaccoData():
    _id: ObjectId
    label: str
    brand: str
    type: str
    weight: float

class Tabacco(Basic):
    # id: int = Field(default_factory = int, alias = "_id")
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    label: str
    brand: str
    type: str
    weight: float = Field(default = 0)
    
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
    

Tabacco.set_collection('tabacco')