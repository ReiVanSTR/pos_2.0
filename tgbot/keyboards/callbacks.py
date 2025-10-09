from aiogram.filters.callback_data import CallbackData
from typing import Optional

from pydantic import Field


class BillsNavigate(CallbackData, prefix = "bills"):
    action: str
    permissions: Optional[str] = Field(default="")

class BillsCommit(CallbackData, prefix = "orders_commit"):
    commit: str #yes, nope

class OrderNavigateCallback(CallbackData, prefix = "order"):
    action: str
    bill_id: Optional[str] = Field(default = "")
    order_id: Optional[str] = Field(default = "")
    tabacco_id: Optional[str] = Field(default="")
    cost: Optional[str] = Field(default="")
    permissions: Optional[str] = Field(default="")
    discount: Optional[str] = Field(default="")



class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    kwargs: Optional[str] = ""

class NumKeyboardCallback(CallbackData, prefix = "num_keyboard"):
    action: str



####
    
class MenuNavigateCallback(CallbackData, prefix = "menu_navigate"):
    button_name: str
    permissions: Optional[str] = ""



###
class StorageNavigate(CallbackData, prefix = "storage"):
    action: str
    permissions: Optional[str] = Field(default="")


class Insert(CallbackData, prefix = "insert"):
    brand_type: Optional[str] = None
    brand_name: Optional[str] = None
    tabacco_name: Optional[str] = None
    commit: Optional[str] = None

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    tabacco_id: Optional[str] = ""

class StorageCommit(CallbackData, prefix = "storage_commit"):
    commit: str #yes, nope

class SessionNavigateCallback(CallbackData, prefix = "session"):
    action: str
    permissions: Optional[str] = None
    bill_id: Optional[str] = None
    order_id: Optional[str] = None


class ReportNavigateCallback(CallbackData, prefix = "report"):
    action: str
    report_id: Optional[str] = None
    user_id: Optional[int] = None
    permissions: Optional[str] = None

class CalendarCallback(CallbackData, prefix = "calendar"):
    action: str
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None