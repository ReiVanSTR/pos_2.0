import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from ..keyboards.orders import orders_menu, orders_commit,\
    OrdersNavigate, OrdersCommit

from ..models import Order
from ..misc.states import NavigateOrders, FormNewOrder

from typing import Union

from datetime import datetime

orders_router = Router()

@orders_router.message(F.text.startswith('/') & F.text.contains("orders"))
async def orders_start(message: Message, state: FSMContext, callback_data = None):
    await state.set_state(NavigateOrders.menu)

    markup = orders_menu()
    await message.answer("Orders:", reply_markup = markup)

@orders_router.callback_query(OrdersNavigate.filter(F.button_name == "new_order"))
async def orders_add_new_order(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(FormNewOrder.input_name)

    await query.message.edit_text("Input order name", reply_markup = None)

@orders_router.message(FormNewOrder.input_name, F.text.is_not(None))
async def orders_new_order_name(message: Message, state: FSMContext):
    await state.set_state(FormNewOrder.confirm)

    await state.set_data(data = {"order_name":message.text.strip()})

    markup = orders_commit(OrdersCommit)
    await message.answer(f"Is correct? \n Table name: {message.text.strip()}", reply_markup = markup)

@orders_router.callback_query(FormNewOrder.confirm, OrdersCommit.filter())
async def orders_new_order_commit(query: CallbackQuery, state: FSMContext, callback_data: OrdersCommit):
    await query.answer()

    if callback_data.commit == "yes":
        data = await state.get_data()

        await Order.create_order(order_name = data["order_name"], user_id = query.from_user.id)

    markup = orders_menu()
    await query.message.edit_text("Orders", reply_markup = markup)