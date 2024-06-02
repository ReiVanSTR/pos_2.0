import logging
from aiogram import Router, F, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from typing import Union


from ..models.user import UserData
from ..keyboards.menu import MenuKeyboards
from ..keyboards.callbacks import MenuNavigateCallback
from ..misc.history_manager import Manager
from ..misc.cache import Cache


from ..misc.states import MenuStates

menu_router = Router()

menu_keyboards = MenuKeyboards()


@menu_router.message(CommandStart())
async def user_start(event: Union[Message, CallbackQuery], user: UserData, cache: Cache, Manager: Manager, logger):
    await Manager.clear()
    await Manager.push(MenuStates.menu.state, {})
    logger.filelog(user.user_id, "Logging in POS")

    markup = await menu_keyboards.menu_keyboard(user = user)
    if isinstance(event, Message):
        await event.delete()
        new_query = await event.answer(f"Hello, {user.username}", reply_markup = markup)
    if isinstance(event, CallbackQuery):
        await event.message.delete()
        new_query = await event.message.answer(f"Hello, {user.username}", reply_markup = markup)

    main_query = await cache.get_main_query(user.user_id)
    if main_query:
        if isinstance(main_query, CallbackQuery):
            await main_query.message.delete()
        
        if isinstance(main_query, Message):
            await main_query.delete()
        
    await cache.set_main_query(user.user_id, new_query)