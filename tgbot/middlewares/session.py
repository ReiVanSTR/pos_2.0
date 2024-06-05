import logging
from typing import Callable, Dict, Any, Awaitable
import asyncio

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.event.handler import CallableObject, HandlerObject

from ..models import SessionData, Session, Permissions
from ..handlers.user import user_start
from ..misc.states import MenuStates, SessionStates
from ..keyboards.menu import MenuKeyboards



class SessionMiddleware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
      
      _current_session = await Session.get_current_session()


      if not _current_session:
        Manager = data["Manager"]
        cache = data["cache"]
        user = data["user"]
        logger = data["logger"]
        state = await data["state"].get_state()

        callback_data_exceptions = [
           "menu_navigate:session:open_session_schedules_access",
           "session:open_session:::"
        ]

        if Permissions.GLOBAL.value in user.permissions:
            return await handler(event, data)


        if isinstance(event, CallbackQuery):
            logging.log(30, event.data)
            if event.data in callback_data_exceptions:
               return await handler(event, data)
            
            if state == MenuStates.menu.state:
                await event.answer("Session not started!", show_alert = True)
                return 
            await event.answer("Session not started!", show_alert = True)
            return await user_start(event, user, cache, Manager, logger)
        
        if isinstance(event, Message):
           if event.text == "/start":
            return await user_start(event, user, cache, Manager, logger)
           
           await event.delete()
           await event.answer("Session not started! \n Use: /start to continue")
           return 

      data["session"] = _current_session
      return await handler(event, data)