import logging
from pydantic import Field
from dataclasses import dataclass
from .basic import Basic, ObjectId
from .bills import Bills, BillData
from typing import List, Dict, Union
from datetime import datetime
from .agregations.count_session_total import pipeline
from .agregations.test import bill_pipeline

@dataclass
class SessionData():
    _id: ObjectId
    start_time: datetime
    end_time: datetime
    opened_by: int
    closed_by: int
    is_closed: bool
    bills: List[ObjectId]


class Session(Basic):
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id") 
    start_time: datetime
    end_time: datetime = Field(default = None)
    opened_by: int
    closed_by: int = Field(default = None)
    is_closed: bool = False
    bills: List = Field(default_factory = List)

    @classmethod
    async def open_session(cls, opened_by: int):
        """
        :param opened_by: telegram user_id
        """
        _current_session = await cls._collection.find_one({"is_closed":False})

        if _current_session:
            raise "Only one session can be started!"

        document: Dict = {
            "start_time":datetime.now(),
            "end_time":None,
            "opened_by":opened_by,
            "closed_by": None,
            "is_closed":False,
            "bills":[],
        }

        await cls._collection.insert_one(document)
    
    @classmethod
    async def close_session(cls, closed_by: int):
        """
        :param opened_by: telegram user_id
        """
        pass

    @classmethod
    async def get_current_session(cls):
        _current_session = await cls._collection.find_one({"is_closed":False})

        return SessionData(**_current_session) if _current_session else None

    @classmethod
    async def push_bill(cls, bill_id: Union[str, ObjectId]):
        if isinstance(bill_id, str):
            bill_id = ObjectId(bill_id)

        await cls._collection.update_one({"is_closed":False}, {"$push":{"bills":bill_id}}, upsert = True)

    @classmethod
    async def count_total(cls):
        async for result in cls._collection.aggregate(pipeline):
            return result

    @classmethod
    async def get_activities(cls):
        _current_session = await cls.get_current_session()

        response = []
        for bill in _current_session.bills:
            logging.log(30, bill)
            async for result in cls._db.bills.aggregate(bill_pipeline(bill)):
                logging.log(30, result)
                response.append(result)

        return response
    
    @classmethod
    async def get_bills(cls):
        _current_session = await cls.get_current_session()
        response = []
        try:
            for bill in _current_session.bills:
                bill_data = await Bills.get_bill(bill)
                if not bill_data.is_closed:
                    response.append(bill_data)
        except:
            pass

        return response
    
    @classmethod
    async def count_documents(cls):
        return len(await cls.get_bills())
    
    @classmethod
    async def update_session_bills(cls, bills_list: List[ObjectId]):
        for bill in bills_list:
            await cls.push_bill(bill)



Session.set_collection("sessions")