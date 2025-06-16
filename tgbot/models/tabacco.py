from pydantic import Field
from typing import Union
from dataclasses import dataclass
from .basic import Basic, ObjectId
from typing import List


@dataclass
class TabaccoData():
    _id: ObjectId
    label: str
    brand: str
    type: str
    weight: float
    is_showed: bool
    used_weight: float = 0.0

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
    is_showed: bool = Field(default = False)

    @classmethod
    async def create_tabacco(cls, label, brand, type):
        document = {
            "label":label,
            "brand":brand,
            "type":type,
            "weight":0,
            "is_showed":False
        }

        obj = await cls._collection.insert_one(document)
        return obj.inserted_id

    @classmethod
    async def get_by_id(cls, id: Union[ObjectId, str]):
        if isinstance(id, str):
            id = ObjectId(id)
        obj = await cls._collection.find_one({'_id': id})
        return TabaccoData(**obj) if obj else None
    
    @classmethod
    async def get_by_label(cls, label: str):
        obj = await cls._collection.find_one({"label":label})
        return TabaccoData(**obj) if obj else None
    
    @classmethod
    async def get_all_brands(cls):
        documents = cls._collection.find()
        return [document["brand"] async for document in documents]
    
    @classmethod
    async def get_all(cls, filtr = {}):
        documents = cls._collection.find(filtr)
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
    async def find_many(cls, field: str, args: List):
        if isinstance(field, str):
            field = ObjectId(field)

        query = {field: {"$in":args}}
        return [TabaccoData(**document) async for document in cls._collection.find(query)]
    
    @classmethod
    async def update_weight(cls, id: Union[ObjectId, str], new_weight):
        if isinstance(id, str):
            id = ObjectId(id)
        
        await cls._collection.update_one({"_id":id}, {"$set":{"weight":new_weight}})

    @classmethod
    async def change_visibility(cls, id):
        if isinstance(id, str):
            id = ObjectId(id)
        current = await cls._collection.find_one({"_id":id}, {"is_showed"})
        
        current = current.get("is_showed")

        await cls._collection.update_one({"_id":id}, {"$set":{"is_showed":not current}})
    

Tabacco.set_collection('tabacco')