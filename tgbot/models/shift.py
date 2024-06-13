from . import ObjectId
from .basic import Basic
from pydantic import Field
from datetime import datetime, timedelta
import pytz

tzinfo = pytz.timezone("Europe/Warsaw")
from dataclasses import dataclass

@dataclass(frozen = True)
class ShiftData():
    _id: ObjectId
    start_time: datetime
    end_time: datetime
    user_id: int
    work_time: datetime = None


class Shift(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id") 
    start_time: datetime
    end_time: datetime = Field(default = None)
    work_time: datetime 
    user_id: int

    @classmethod
    async def is_exists(cls, user_id: int) -> bool:
        result = await cls._collection.find_one({"user_id":user_id, "end_time":None})

        return True if result else False

    @classmethod
    async def open_shift(cls, user_id: int):
        is_exists =  await cls.is_exists(user_id)

        if is_exists:
            return None

        document = {
            "user_id":user_id,
            "start_time": datetime.now(pytz.utc),
            "end_time": None,
            "work_time":None,
        }

        inserted_id = await cls._collection.insert_one(document)
        return inserted_id


    @classmethod
    async def find_shift_by_date(cls, date, user_id):
        next_day = date + timedelta(days = 1)
        pipeline = [
            {
                '$match': {
                    'end_time': {
                        '$gte': datetime(date.year, date.month, date.day, 0, 0, 0), #tzinfo=tzinfo), 
                        '$lt': datetime(next_day.year, next_day.month, next_day.day, 6, 0, 0) # tzinfo=tzinfo)
                    },
                    'user_id': user_id
                }
            }
        ]

        result = cls._collection.aggregate(pipeline)

        if result:
            shift = []
            async for res in result:
                shift.append(res)

            return ShiftData(**shift[0]) if shift else None

        return None
    
    @classmethod
    async def find_current_shift_by_user_id(cls, user_id):
        pipeline = [
            {
                '$match': {
                    'end_time': None,
                    'user_id': user_id
                }
            }
        ]

        result = cls._collection.aggregate(pipeline)

        if result:
            shift = []
            async for res in result:
                shift.append(res)

            return ShiftData(**shift[0]) if shift else None

        return None
    
    @classmethod
    async def close_shift(cls, user_id):
        _work_time = await cls.current_shift_time(user_id)
        _current_shift = await cls.find_current_shift_by_user_id(user_id)
        _current_time = datetime.now(pytz.utc)
        if _work_time:
            await cls._collection.update_one(
                {"_id":_current_shift._id},
                {"$set":{"end_time":_current_time, "work_time":{"hours":_work_time.get("hours"), "minutes":_work_time.get("minutes")}}}
            )

            return _current_shift._id

        return None


    @classmethod
    async def current_shift_time(cls, user_id):
        current_shift = await cls.find_current_shift_by_user_id(user_id)
        if current_shift:
            _current_time = datetime.now(pytz.utc)

            timed = _current_time - pytz.utc.localize(current_shift.start_time)
            hours, reminder = divmod(timed.seconds, 3600)
            minutes, _ = divmod(reminder, 60)

            return {"hours":hours, "minutes":minutes}
        
        return None
    
    @classmethod
    async def find_opened_shifts(cls):
        date = datetime.now(pytz.utc)
        response = await cls._collection.find_one(
            {"start_time": {"$gte": date}, "end_time":None}
        )

        if response:
            return True
        
        return False




Shift.set_collection("shifts")