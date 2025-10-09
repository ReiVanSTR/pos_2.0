import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from ..models import User, UserData, Session, Permissions, Shift, Post

from .callbacks import MenuNavigateCallback
from .pager import BasicPageGenerator

import pytz
timezone = pytz.timezone("Europe/Warsaw")

class MenuKeyboards():
    async def menu_keyboard(self, user: UserData):
        keyboard = InlineKeyboardBuilder()

        user_info_button = InlineKeyboardBuilder().button(
                                                text = f"Logined as {user.username}, {user.post.name}", callback_data = MenuNavigateCallback(button_name = "open_stat"))
        user_info_button.adjust(1)
        keyboard.attach(user_info_button)

        bills_quantity = await Session.count_documents()
        bills_button = InlineKeyboardBuilder().button(
                                                text = f"Bills ({bills_quantity})", 
                                                callback_data = MenuNavigateCallback(button_name = "bills"))
        bills_button.adjust(1)
        keyboard.attach(bills_button)

        row = InlineKeyboardBuilder()
        row.button(text = "Storage", callback_data = MenuNavigateCallback(button_name = "storage", permissions = Permissions.OPEN_STORAGE.value))
        row.button(text = "Mixes",callback_data = MenuNavigateCallback(button_name = "mixes"))
        row.adjust(2)
        keyboard.attach(row)

        row = InlineKeyboardBuilder()
        row.button(text = "Invent", callback_data = MenuNavigateCallback(button_name = "invent", permissions = Permissions.INVENTARIZE_STORAGE.value))
        row.button(text = "Session",callback_data = MenuNavigateCallback(button_name = "session", permissions = Permissions.OPEN_SESSION.value))
        row.adjust(2)
        keyboard.attach(row)

        options_button = InlineKeyboardBuilder().button(
                                                text = f"Options⚙️", 
                                                callback_data = MenuNavigateCallback(button_name = "test"))
        options_button.adjust(1)
        keyboard.attach(options_button)

        if Permissions.GLOBAL.value in user.permissions or user.post == Post.Admin:
            reports_button = InlineKeyboardBuilder().button(
                                                    text = f"Reports📊", 
                                                    callback_data = MenuNavigateCallback(button_name = "reports", permissions = Permissions.GLOBAL.value))
            reports_button.adjust(1)
            keyboard.attach(reports_button)

        return keyboard.as_markup()


    async def menu_user_statictics(self, user: UserData):
        _work_time = await Shift.current_shift_time(user.user_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text = f"Current shift time: {_work_time.get('hours')}h {_work_time.get('minutes')}m",
            callback_data = MenuNavigateCallback(button_name = "static")
        )
        keyboard.button(
            text = "Close shift",
            callback_data = MenuNavigateCallback(button_name = "user_statistics_close")
        )

        keyboard.button(
            text = "<<",
            callback_data = MenuNavigateCallback(button_name = "back")
        )

        keyboard.adjust(1, repeat = True)

        return keyboard.as_markup()

    async def menu_start_shift(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text = f"Now: {datetime.now(tz = timezone).strftime('%D-%H-%M')}",
            callback_data = MenuNavigateCallback(button_name = "static")
        )
        keyboard.button(
            text = "Open shift",
            callback_data = MenuNavigateCallback(button_name = "user_statistics")
        )
        keyboard.button(
            text = "<<",
            callback_data = MenuNavigateCallback(button_name = "back")
        )

        keyboard.adjust(1, repeat = True)

        return keyboard.as_markup()