from pydantic import Field
from enum import Enum
from typing import Union
from dataclasses import dataclass
from tgbot.models.basic import Basic, ObjectId
from typing import List


class Post(Enum):
    Waiter = 1
    HokahMaster = 2
    Menager = 3
    Admin = 0 

    def __repr__(self):
        return self._name_
    
    def get_post(self):
        return {"post_name":self._name_, "post_value":self._value_}

class HoursMenager():
    def __init__(self, work_hours) -> None:
        self.work_hours = work_hours

@dataclass
class UserData:
    _id: ObjectId
    user_id: int
    username: str
    post: Post
    work_hours: HoursMenager

    def __init__(self, _id, user_id, username, post, work_hours):
        self._id = _id
        self.user_id = user_id
        self.username = username
        self.post = Post(post)
        self.work_hours = HoursMenager(work_hours)


class User(Basic):
    _id: ObjectId
    user_id: int
    username: str
    post: Post
    work_hours: List

    @classmethod
    async def is_exists(cls, user_id):
        result = await cls._collection.find_one({"user_id":user_id})

        return True if result else False

    @classmethod
    async def create_user(cls, user_id: int, username: str, post: int):
        if await cls.is_exists(user_id):
            return cls.get_user_by_user_id(user_id)
            
        document = {
            "user_id": user_id,
            "username": username,
            "post": post,
            "work_hours": [],
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
    @classmethod
    async def get_user_by_user_id(cls, user_id):
        document = await cls._collection.find_one({"user_id":user_id})

        return UserData(**document)

    
User.set_collection("Users")