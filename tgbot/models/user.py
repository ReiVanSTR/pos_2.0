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


class Permissions(Enum):
    GLOBAL = "global_access"

    OPEN_STORAGE = "open_storage_access"
    INVENTARIZE_STORAGE = "inventarize_storage_access"    
    OPEN_SESSION = "open_session_schedules_access"

    BILLS_REMOVE_BILL = "bills_remove_bill_access"
    ORDERS_REMOVE_ORDER = "orders_remove_order_access"
    HAND_OVER_BILL = "hand_over_bill_access"

    SESSION_OPEN_BILL = "session_open_bill"

    def __repr__(self):
        return self.value

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
    permissions: List
    shift_cost: int
    hour_price: int
    selling_reward: int

    def __init__(self, _id, user_id, username, post, work_hours, permissions, shift_cost, hour_price, selling_reward) -> None:
        self._id = _id
        self.user_id = user_id
        self.username = username
        self.post = Post(post)
        self.work_hours = HoursMenager(work_hours)
        self.permissions = permissions
        self.shift_cost = shift_cost
        self.hour_price = hour_price
        self.selling_reward = selling_reward


class User(Basic):
    _id: ObjectId
    user_id: int
    username: str
    post: Post
    work_hours: List
    permissions: List
    shift_cost: int
    hour_price: int
    selling_reward: int

    @classmethod
    async def is_exists(cls, user_id):
        result = await cls._collection.find_one({"user_id":user_id})

        return True if result else False

    @classmethod
    async def create_user(cls, user_id: int, username: str, post: int, shift_cost: int = 150, hour_price: int = 22, selling_reward: int = 5):
        if await cls.is_exists(user_id):
            return await cls.get_user_by_user_id(user_id)
            
        document = {
            "user_id": user_id,
            "username": username,
            "post": post,
            "work_hours": [],
            "permissions": [],
            "shift_cost": shift_cost,
            "hour_price": hour_price,
            "selling_reward": selling_reward,
        }

        inserted_document = await cls._collection.insert_one(document)
        return inserted_document.inserted_id
    
    @classmethod
    async def get_user_by_user_id(cls, user_id):
        document = await cls._collection.find_one({"user_id":user_id})

        return UserData(**document)
    
    @classmethod
    async def grand_permission(cls, user_id, permission: Permissions):
        await cls._collection.update_one({"user_id":user_id}, {"$push":{"permissions":permission.value}})

    @classmethod
    async def update_shift(cls, user_id: int, shift_id: ObjectId):
        await cls._collection.update_one({"user_id":user_id}, {"$push":{"work_hours":shift_id}})

    @classmethod
    async def get_all_users(cls):
        users = []
        async for user in cls._collection.find({}):
            users.append(UserData(**user))
        
        return users
        

    
User.set_collection("Users")