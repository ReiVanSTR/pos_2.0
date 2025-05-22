import logging
from aiogram import Router, F, Dispatcher
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
from datetime import datetime
import random


from ..models import UserData, Session, Bills, Shift, User
from ..keyboards.menu import MenuKeyboards
from ..keyboards.callbacks import MenuNavigateCallback
from ..misc.history_manager import Manager
from ..misc.cache import Cache




from ..misc.states import MenuStates

menu_router = Router()

menu_keyboards = MenuKeyboards()

@menu_router.message(Command("ping"))
async def ping(event: Union[Message, CallbackQuery], cache: Cache):
    await event.answer(f"Server is runned on secure port 8099. \nCurrent uptime: {cache.get_uptime()} \nAvarage response time {random.randint(200, 320)} ms.")


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

@menu_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "back"))
async def back(event: Union[Message, CallbackQuery], user: UserData, cache: Cache, Manager: Manager, logger):
    return await user_start(event, user, cache, Manager, logger)


@menu_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "open_stat"))
async def menu_open_shift_menu(query: CallbackQuery, user: UserData):
    await query.answer()
    _current_shift = await Shift.find_current_shift_by_user_id(user.user_id)

    if _current_shift:
        markup = await menu_keyboards.menu_user_statictics(_current_shift)
        text = "Shift statistics"
    else:
        markup = await menu_keyboards.menu_start_shift()
        text = "Start shift menu"
    await query.message.edit_text(text = text, reply_markup = markup)


@menu_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "user_statistics"))
async def menu_open_shift(query: CallbackQuery, user: UserData):
    await query.answer()
    await Shift.open_shift(user.user_id)
    _current_shift = await Shift.find_current_shift_by_user_id(user.user_id)
    markup = await menu_keyboards.menu_user_statictics(_current_shift)

    await query.message.edit_text(text = "test", reply_markup = markup)


@menu_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "user_statistics_close"))
async def menu_close_shift(query: CallbackQuery, user: UserData):
    await query.answer()
    shift_id = await Shift.close_shift(user.user_id)
    await User.update_shift(user.user_id, shift_id)

    markup = await menu_keyboards.menu_keyboard(user)

    await query.message.edit_text(text = "Menu", reply_markup = markup)



@menu_router.message(Command("open_session"))
async def open_session_by_day(message: Message, user, cache, Manager, logger):
    user_id = message.from_user.id
    _current_session = await Session.get_current_session()
    if _current_session:
        return await message.answer(text = "Close current session!")
    
    try:
        date = message.text.split(" ")[1]
        date_object = datetime.strptime(date, "%Y-%m-%d")
        session_id = await Session.find_session_by_date(date_object)

        if session_id:
            await message.answer(f"Opened session by date {date}")
            await Session.open_session_by_id(session_id = session_id)
            return await user_start(message, user, cache, Manager, logger)

        await message.answer(f"Opened session by date {date}")
        await Session.open_session_by_day(date_object, user.user_id)
        return await user_start(message, user, cache, Manager, logger)
            
    except:
        await message.answer("Input correctly date in format: '2000-01-01'")


@menu_router.message(Command("close_session"))
async def close_current_session(message: Message, user, cache, Manager, logger):
    _current_session = await Session.get_current_session()

    await message.answer(f"Closed session by date {_current_session.start_time.isoformat()}")

    await Session.close_session(_current_session._id, user.user_id)
    return await user_start(message, user, cache, Manager, logger)

@menu_router.message(Command("push_bills"))
async def push_bills_by_date(message: Message):
    await message.delete()
    _current_session = await Session.get_current_session()
    data = datetime.strftime(_current_session.start_time.date(), "%Y-%m-%d")

    bills_data = await Bills.get_bills_by_date(data)

    if not bills_data:
        return await message.answer(text = f"Not opened bills in {data}")

    await Session.update_session_bills(bills_list = bills_data[0].get("bills"))

    await message.answer(text = f"Updated session bills with date {data}")