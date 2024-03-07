import logging
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict
from .basic import BasicKeyboard, BasicKeyboardList
from ..misc.database import DB, rc

from ..models import Tabacco

database = DB(rc)
  
menu = ["Add", "Invent", "Show"]

brand_types = ["Standart", "Premium", "Mix"]

class StorageNavigate(CallbackData, prefix = "storage"):
    button_name: str
    type: str #category, sub-category

class Insert(CallbackData, prefix = "insert"):
    brand_type: Optional[str] = None
    brand_name: Optional[str] = None
    tabacco_name: Optional[str] = None
    other: Optional[Dict] = None

# class BasicKeyboard:
#     def __init__(self, name, next, prev, contains = List):
#         self.name = name # {category}:{subcategory}
#         self.next = next
#         self.prev = prev
#         self.contains = contains

# class BasicKeyboardList:
#     root = None
#     end = None
    
#     def insert_root(self, name):
#         if self.root == None:
            


menu_kb = BasicKeyboardList()

kb_1 = InlineKeyboardBuilder()
for button in menu:

    kb_1.button(
        text = button,
        callback_data = StorageNavigate(name = button.lower(), type = "category")
    )

menu_kb.insert_root("storage_menu", kb_1.as_markup())

select_type_kb = InlineKeyboardBuilder()
for button in brand_types:
    select_type_kb.button(
        text = button,
        callback_data = Insert(brand_type = button),
        next_name = button.lower()
    )

async def select_brand_kb(type: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    brands = await Tabacco.get_all_brands_by_type(type)
    logging.log(30, type)
    for brand in brands:
        logging.log(30, brand)
        kb.button(
            text = brand,
            callback_data = Insert(brand_name = brand)
        )

    kb.button(
        text = "<<",
        callback_data = StorageNavigate(name = "add", type = "category")
    )

    return kb.as_markup()
invent_kb = InlineKeyboardBuilder()
show_kb = InlineKeyboardBuilder()

