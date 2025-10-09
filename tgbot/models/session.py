import logging
from pydantic import Field
from dataclasses import dataclass
from .basic import Basic, ObjectId
from .bills import Bills, BillData
from typing import List, Dict, Union
from datetime import datetime
from .agregations.count_session_total import get_total
from .agregations.test import bill_pipeline
from .agregations.get_session_by_date import get_pipeline
from .agregations.session_report import report_aggregation, total_report_aggregation
from datetime import timedelta
from ..services.reports.session_dataclasses import SessionReportData

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
            return "Only one session can be started!"
        

        document: Dict = {
            "start_time":datetime.now(),
            "end_time":None,
            "opened_by":opened_by,
            "closed_by": None,
            "is_closed":False,
            "bills":[],
        }

        await cls._collection.insert_one(document)
        return await cls.get_current_session()
    
    @classmethod
    async def open_session_by_id(cls, session_id: Union[str, ObjectId]):
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)

        await cls._collection.update_one({"_id":session_id}, {"$set":{"is_closed":False}})
        return session_id.__str__()
    

    @classmethod
    async def open_session_by_day(cls, date, user_id):
        """
        :param opened_by: telegram user_id
        """
        _current_session = await cls._collection.find_one({"is_closed":False})

        if _current_session:
            return "Only one session can be started!"
        
        start_time = date + timedelta(hours = 8)
        end_time = start_time + timedelta(hours = 1)

        document = {
            "start_time":start_time,
            "end_time":end_time,
            "opened_by":user_id,
            "closed_by": None,
            "is_closed":False,
            "bills":[],
        } #type: ignore

        res = await cls._collection.insert_one(document)
        return res.inserted_id

    
    @classmethod
    async def close_session(cls, session_id: Union[str, ObjectId], closed_by: int):
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)

        await cls._collection.update_one({"_id":session_id}, {"$set":{"is_closed":True, "closed_by":closed_by}})


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
    async def count_total(cls, session_id):
        async for result in cls._collection.aggregate(get_total(session_id = session_id)):
            return result

    @classmethod
    async def get_activities(cls):
        _current_session = await cls.get_current_session()

        response = []
        for bill in _current_session.bills:
            async for result in cls._db.bills.aggregate(bill_pipeline(bill)):
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
    async def get_bills_by_session_id(cls, session_id: Union[str, ObjectId]):
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)

        _current_session = await cls._collection.find_one({"_id":session_id})

        if not _current_session:
            return f"Session not found {session_id}" 
        
        _current_session = SessionData(**_current_session)

        response = []
        try:
            for bill in _current_session.bills:
                bill_data = await Bills.get_bill(bill)
                response.append(bill_data)
        except Exception as e:
            print(e)

        return response
    
    @classmethod
    async def count_documents(cls):
        return len(await cls.get_bills())
    

    @classmethod
    async def update_session_bills(cls, bills_list: List[ObjectId]):
        for bill in bills_list:
            await cls.push_bill(bill)

    @classmethod
    async def close_current_session(cls, user_id, end_time = None):
        _current_session = await cls.get_current_session()
        
        await cls._collection.update_one({"_id":_current_session._id}, {"$set":{"is_closed":True, "closed_by":user_id, "end_time":datetime.now()}})


    @classmethod
    async def find_session_by_date(cls, date):
        pipeline = get_pipeline(date)
        result = cls._collection.aggregate(pipeline)

        if result:
            session = []
            async for res in result:
                session.append(res)

            return session[0]["_id"] if session else None

        return None

    @classmethod
    async def generate_report_data(cls, session_id):
        pipeline = report_aggregation(session_id)
        result = cls._collection.aggregate(pipeline)

        if result:
            session_data = []
            async for res in result:
                session_data.append(res)

            return SessionReportData(session_data) if session_data else None

        return None
    
    @classmethod
    async def generate_pereodic_report_data(cls, from_date, to_date):
        pipeline = total_report_aggregation(from_date, to_date)
        result = cls._collection.aggregate(pipeline)

        if result:
            session_data = []
            async for res in result:
                session_data.append(res)

            return SessionReportData(session_data) if session_data else None

        return None
 
Session.set_collection("sessions")