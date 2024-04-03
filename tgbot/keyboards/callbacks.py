from aiogram.filters.callback_data import CallbackData
from typing import Optional

from pydantic import Field

class BillsNavigateCallback(CallbackData, prefix = "bills"):
    """
    _navigate_callback 'class BillKeyboards'
    """
    button_name: str
    type: str #category, sub-category

class BillsCommit(CallbackData, prefix = "orders_commit"):
    commit: str #yes, nope

class OrderNavigateCallback(CallbackData, prefix = "order"):
    action: str
    bill_id: Optional[str] = Field(default = "")
    order_id: Optional[str] = Field(default = "")

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    kwargs: Optional[str] = Field(default = " ")

class NumKeyboardCallback(CallbackData, prefix = "num_keyboard"):
    action: str



####
    
class MenuNavigateCallback(CallbackData, prefix = "menu_navigate"):
    button_name: str