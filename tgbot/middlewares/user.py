from multiprocessing.util import is_exiting
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from ..models import User, UserData

class UserMiddleware(BaseMiddleware):
    # def __init__(self, config) -> None:
    #     self.config = config

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not await User.is_exists(event.from_user.id):
            return
        
        user = await User.get_user_by_user_id(event.from_user.id)
        data["user"] = user
        return await handler(event, data)