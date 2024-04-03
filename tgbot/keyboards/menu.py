import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict, Union
from datetime import datetime

from ..models import User, UserData, Bills

from .callbacks import MenuNavigateCallback
from .pager import BasicPageGenerator

class MenuKeyboards():
    async def menu_keyboard(self, user: UserData):
        keyboard = InlineKeyboardBuilder()

        user_info_button = InlineKeyboardBuilder().button(
                                                text = f"Logined as {user.username}, {user.post.name}", callback_data = MenuNavigateCallback(button_name = "static"))
        user_info_button.adjust(1)
        keyboard.attach(user_info_button)

        bills_quantity = await Bills.count_documents({"is_closed":False})
        bills_button = InlineKeyboardBuilder().button(
                                                text = f"Bills ({bills_quantity})", 
                                                callback_data = MenuNavigateCallback(button_name = "bills"))
        bills_button.adjust(1)
        keyboard.attach(bills_button)

        row = InlineKeyboardBuilder()
        row.button(text = "Storage", callback_data = MenuNavigateCallback(button_name = "storage"))
        row.button(text = "Mixes",callback_data = MenuNavigateCallback(button_name = "mixes"))
        row.adjust(2)
        keyboard.attach(row)

        row = InlineKeyboardBuilder()
        row.button(text = "Invent", callback_data = MenuNavigateCallback(button_name = "invent"))
        row.button(text = "Session",callback_data = MenuNavigateCallback(button_name = "session"))
        row.adjust(2)
        keyboard.attach(row)

        options_button = InlineKeyboardBuilder().button(
                                                text = f"Options⚙️", 
                                                callback_data = MenuNavigateCallback(button_name = "bills"))
        options_button.adjust(1)
        keyboard.attach(options_button)

        return keyboard.as_markup()


