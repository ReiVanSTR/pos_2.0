from typing import Union
from motor.motor_tornado import MotorCollection
from pydantic import BaseModel
from loader import db
import binascii

from bson.objectid import ObjectId as BsonObjectId


class ObjectId(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, BsonObjectId):
            raise TypeError('ObjectId required')
        return str(v)
    
    def __str__(self) -> str:
        return binascii.hexlify(self.__id).decode()


class Basic(BaseModel):
    _collection: MotorCollection = None

    @classmethod
    def set_collection(self, collection: str):
        self._collection = db[collection]
        self._db = db
    
    @classmethod
    async def count(cls):
        num = await cls._collection.count_documents({})
        return num

    @classmethod
    async def get(cls, id: Union[ObjectId, str]):
        if isinstance(id, str):
            id = ObjectId(id)
        obj = await cls._collection.find_one({'_id': id})
        return cls(**obj) if obj else None

    @classmethod
    async def get_all(cls):
        objs = cls._collection.find()
        return [cls(**u) async for u in objs]

    @classmethod
    async def update(cls, id: int, **kwargs):
        await cls._collection.find_one_and_update({'_id': id}, {'$set': kwargs})
        return await cls.get(id)

    @classmethod
    async def create(cls, **kwargs):
        # if '_id' not in kwargs:
        #     kwargs["_id"] = await cls.count() + 1
        obj = cls(**kwargs)
        obj = await cls._collection.insert_one(obj.model_dump(by_alias=True))
        return await cls.get(obj.inserted_id)