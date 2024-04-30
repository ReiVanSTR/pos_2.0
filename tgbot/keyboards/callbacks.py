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

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    kwargs: Optional[str] = ""

class NumKeyboardCallback(CallbackData, prefix = "num_keyboard"):
    action: str



####
    
class MenuNavigateCallback(CallbackData, prefix = "menu_navigate"):
    button_name: str