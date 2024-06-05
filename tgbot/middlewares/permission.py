import logging
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from ..keyboards.callbacks import BillsNavigate, MenuNavigateCallback, OrderNavigateCallback
from ..models import User, Permissions

def parse_command(str: str):
    if str.startswith("/"):
        res = str.split(" ")
        return res[0][1:]
    
    return None

class PermissionsMiddleware(BaseMiddleware):
    callback_list = {
            "bills":BillsNavigate,
            "order":OrderNavigateCallback,
            "menu_navigate":MenuNavigateCallback,
        }

    commands_list = [
        "open_session",
        "close_session",
        "push_bills"
    ]
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        if isinstance(event, CallbackQuery):
            prefix = event.data.split(":")[0]
            callback = self.callback_list.get(prefix, None)

            if callback:
                callback_data = callback.unpack(event.data)

                if not callback_data.permissions:
                    return await handler(event, data)
                
                user = await User.get_user_by_user_id(event.from_user.id)
                
                if isinstance(event, Message):
                    command = parse_command(event.text)

                    if command:
                        if command in self.commands_list:
                            if Permissions.GLOBAL.value in user.permissions:
                                return await handler(event, data)
                
                if callback_data.permissions in user.permissions:
                    return await handler(event, data)

                await event.answer(text = f"You have not permited to {callback_data.permissions}", show_alert = True)
                return
            
        return await handler(event, data)