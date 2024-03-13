import logging
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict

from ..models import Order

class OrdersNavigate(CallbackData, prefix = "orders"):
    button_name: str
    type: str #category, sub-category

class OrdersCommit(CallbackData, prefix = "orders_commit"):
    commit: str #yes, nope

def orders_commit(callback):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text = "Yes",
        callback_data = callback(commit = "yes")
    )

    keyboard.button(
        text = "Nope",
        callback_data = callback(commit = "no")
    )
    keyboard.adjust(1,1)
    return keyboard.as_markup()

def orders_menu():
    menu = ["New order", "Orders"]
    keyboard = InlineKeyboardBuilder()

    for menu_button in menu:
        keyboard.button(
            text = menu_button,
            callback_data = OrdersNavigate(button_name = menu_button.replace(" ", "_").lower(), type = "category")
        )

    return keyboard.as_markup()