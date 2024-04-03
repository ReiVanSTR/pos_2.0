import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from ..middlewares.user import UserMiddleware
from ..models.user import UserData
from ..keyboards.menu import MenuKeyboards
from ..keyboards.callbacks import MenuNavigateCallback

menu_router = Router()
menu_router.message.middleware(UserMiddleware())
menu_router.callback_query.middleware(UserMiddleware())
menu_keyboards = MenuKeyboards()


@menu_router.message(CommandStart())
async def user_start(message: Message, user: UserData):

    markup = await menu_keyboards.menu_keyboard(user = user)
    await message.answer(f"Hello, {user.username}", reply_markup = markup)

@menu_router.callback_query(MenuNavigateCallback.filter(F.button_name == "main_menu"))
async def user_back(query: CallbackQuery, user: UserData):

    markup = await menu_keyboards.menu_keyboard(user = user)
    await query.message.edit_text(f"Hello, {user.username}", reply_markup = markup)