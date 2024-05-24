import logging
from aiogram import Router, F, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ..models.user import UserData
from ..keyboards.menu import MenuKeyboards
from ..keyboards.callbacks import MenuNavigateCallback
from ..misc.history_manager import Manager
from ..misc.cache import Cache

from ..misc.states import MenuStates

menu_router = Router()

menu_keyboards = MenuKeyboards()


@menu_router.message(CommandStart())
async def user_start(message: Message, user: UserData, cache: Cache, Manager: Manager):
    await Manager.clear()
    await Manager.push(MenuStates.menu.state, {})
    await message.delete()

    main_query = await cache.get_main_query(user.user_id)
    if main_query:
        if isinstance(main_query, CallbackQuery):
            await main_query.message.delete()
        
        if isinstance(main_query, Message):
            await main_query.delete()
        
    markup = await menu_keyboards.menu_keyboard(user = user)
    new_query = await message.answer(f"Hello, {user.username}", reply_markup = markup)
    await cache.set_main_query(user.user_id, new_query)

# @menu_router.callback_query(StateFilter(MenuStates.menu))
# async def callback_user_start(message: Message, user: UserData, state:FSMContext, HistoryManager: HistoryManager):
#     await state.set_state(MenuStates.menu)
#     await HistoryManager.clear()
#     await HistoryManager.push(MenuStates.menu.state, {})
#     markup = await menu_keyboards.menu_keyboard(user = user)
#     await message.answer(f"Hello, {user.username}", reply_markup = markup)

async def input_label(query: CallbackQuery, bot ,dispatcher: Dispatcher):
    await dispatcher.feed_raw_update(bot, {"input_message":"bla bla bla"})



@menu_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "test"))
async def catch(query: CallbackQuery, bot, dispatcher):
    logging.log(30, bot, dispatcher)

    await input_label(query, bot, dispatcher)


