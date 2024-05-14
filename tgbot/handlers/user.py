import logging
from aiogram import Router, F, Dispatcher
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery, WebAppData, Update
from aiogram.fsm.context import FSMContext
from ..middlewares.user import UserMiddleware
from ..models.user import UserData
from ..keyboards.menu import MenuKeyboards
from ..keyboards.callbacks import MenuNavigateCallback
from aiogram.fsm.scene import HistoryManager

from ..misc.states import MenuStates, BillStates

menu_router = Router()

menu_keyboards = MenuKeyboards()


@menu_router.message(CommandStart())
async def user_start(message: Message, user: UserData, state:FSMContext, HistoryManager: HistoryManager):
    await state.set_state(MenuStates.menu)
    await HistoryManager.clear()
    await HistoryManager.push(MenuStates.menu.state, {})
    markup = await menu_keyboards.menu_keyboard(user = user)
    await message.answer(f"Hello, {user.username}", reply_markup = markup)

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


