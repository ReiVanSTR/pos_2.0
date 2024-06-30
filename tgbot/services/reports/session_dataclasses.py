from dataclasses import dataclass
from tgbot.models.user import UserData, ObjectId
from datetime import datetime
from pydantic import Field
from typing import Dict, List


@dataclass(init = False)
class SessionEvent:
    user_data: UserData
    timestamp: datetime

    def __init__(self, user_data, timestamp) -> None:
        self.user_data = UserData(**user_data)
        self.timestamp = timestamp

@dataclass(init = False)
class SessionActiveTime:
    hours: int
    minutes: int

    def __init__(self, session_time) -> None:
        self.hours, self.minutes = divmod(session_time, 60)



@dataclass(init = False)
class SessionData:
    session_id: ObjectId
    opened_by: SessionEvent
    closed_by: SessionEvent
    session_active_time: SessionActiveTime

    def __init__(self, raw_session_data):
        self.session_id = ObjectId(raw_session_data.get("_id"))
        self.opened_by = SessionEvent(**raw_session_data.get("opened_by")[0])
        self.closed_by = SessionEvent(**raw_session_data.get("closed_by")[0])
        self.session_active_time = SessionActiveTime(raw_session_data.get("session_time"))

@dataclass
class BillShortData:
    bill_name: str
    bill_cost: int
    orders_count: int


@dataclass(init = False)
class EmployerSellings:
    employer_name: str 
    bills: List[Dict]
    bills_by_card: List[BillShortData]
    card_total: int
    bills_by_cash: List[BillShortData]
    cash_total: int
    chief: List[BillShortData]
    chief_total: int
    total_sellings: int
    total_orders: int

    def __init__(
            self,
            _id,
            bills,
            bills_by_card,
            card_total,
            bills_by_cash,
            cash_total,
            chief,
            chief_total,
            total_sellings,
            total_orders
        ) -> None:
        self.employer_name = _id
        self.bills = bills
        self.bills_by_card = []
        self.card_total = card_total
        self.bills_by_cash = []
        self.cash_total = cash_total
        self.chief = []
        self.chief_total = chief_total
        self.total_sellings = total_sellings
        self.total_orders = total_orders

        for bill in bills_by_card:
            self.bills_by_card.append(BillShortData(**bill))

        for bill in bills_by_cash:
            self.bills_by_cash.append(BillShortData(**bill))
        
        for bill in chief:
            self.chief.append(BillShortData(**bill))
    

@dataclass(init = False)
class TabaccoShortData:
    label: str
    total_used: int

    def __init__(self, _id, tabacco_data, total_used):
        self.label = _id
        self.total_used = total_used

@dataclass(init = False)
class Shift:
    username: str
    total_hours: int
    total_minutes: int

    def __init__(self, _id, work_time, total_hours, total_minutes) -> None:
        self.username = _id
        self.total_hours = total_hours
        self.total_minutes = total_minutes

@dataclass(init = False)
class SessionReportData:
    session_data: SessionData
    employer_sellings: List[EmployerSellings]
    total_selling_by_card: int
    total_selling_cash: int
    total_selling_chief: int
    tabacco_data: List[TabaccoShortData]
    total_tabacco: int
    shifts: List[Shift]

    def __init__(self, raw_data) -> None:
        self.session_data = SessionData(raw_data[0]["session_data"])
        self.employer_sellings = []
        self.total_selling_by_card = raw_data[0].get("total_selling_by_card", 0)
        self.total_selling_cash = raw_data[0].get("total_selling_cash", 0)
        self.total_selling_chief = raw_data[0].get("total_selling_chief", 0)
        self.tabacco_data = []
        self.total_tabacco = raw_data[0].get("total_tabacco", 0)
        self.shifts = []

        for employer in raw_data[0]["employers_selling"]:
            self.employer_sellings.append(EmployerSellings(**employer))

        for tabacco in raw_data[0]["tabacco_data"]:
            self.tabacco_data.append(TabaccoShortData(**tabacco))

        for shift in raw_data[0]["work_hours"]["shifts"]:
            self.shifts.append(Shift(**shift))

    def find_shift(self, username: str):
        for shift in self.shifts:
            return shift if shift.username == username else None