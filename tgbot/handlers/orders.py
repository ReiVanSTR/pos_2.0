from ast import Or
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import OrderCallbackData

from ..keyboards.orders import BillKeyboards
from ..keyboards.callbacks import BillsCommit, BillsNavigateCallback, NavigatePageKeyboard, OrderNavigateCallback, NumKeyboardCallback

from ..models import Order, Bills, Tabacco
from ..misc.states import NavigateBills, FormNewBill, EditBill

from typing import Union

from datetime import datetime

orders_router = Router()

bill_keyboards = BillKeyboards()

@orders_router.message(F.text.startswith('/') & F.text.contains("bills"))
async def bills_start(message: Message, state: FSMContext, callback_data = None):
    await state.set_state(NavigateBills.menu)

    markup = bill_keyboards.bills_menu()
    await message.answer("Bills:", reply_markup = markup)

@orders_router.callback_query(BillsNavigateCallback.filter(F.button_name =="main"))
async def bills_start_callback(query: CallbackQuery, state: FSMContext):
    await state.set_state(NavigateBills.menu)

    markup = bill_keyboards.bills_menu()
    await query.message.edit_text("Bills:", reply_markup = markup)

@orders_router.callback_query(BillsNavigateCallback.filter(F.button_name == "new_bill"))
async def bills_add_new_order(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(FormNewBill.input_name)

    await query.message.edit_text("Input bill name", reply_markup = None)

@orders_router.message(FormNewBill.input_name, F.text.is_not(None))
async def bills_new_bill_name(message: Message, state: FSMContext):
    await state.set_state(FormNewBill.confirm)

    await state.set_data(data = {"order_name":message.text.strip()})

    markup = bill_keyboards.bills_commit()
    await message.answer(f"Is correct? \n Table name: {message.text.strip()}", reply_markup = markup)

@orders_router.callback_query(FormNewBill.confirm, BillsCommit.filter())
async def bills_new_bill_commit(query: CallbackQuery, state: FSMContext, callback_data: BillsCommit):
    await query.answer()

    if callback_data.commit == "yes":
        data = await state.get_data()

        await Bills.create_bill(bill_name = data["order_name"], user_id = query.from_user.id)

    markup = bill_keyboards.bills_menu()
    await query.message.edit_text("Bills", reply_markup = markup)


bill_keyboards.connect_router(orders_router)
bill_keyboards.register_handler(bill_keyboards.navigate_page_slider, [NavigateBills.show_orders, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])

@orders_router.callback_query(BillsNavigateCallback.filter(F.button_name == "bills"))
async def orders_add_new_order(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(NavigateBills.show_orders)

    bill_keyboards.update(data = await Bills.get_all_bills({"is_closed":False}))    
    await state.set_data(data = {"current_page":1})
    markup = bill_keyboards.bills_list()

    await query.message.edit_text("Bill", reply_markup = markup)

@orders_router.callback_query(OrderNavigateCallback.filter(F.action == "open_bill"))
async def orders_open_bill(query: CallbackQuery, state: FSMContext, callback_data: OrderNavigateCallback):
    await query.answer()
    await state.set_state(NavigateBills.show_orders)
    data = await state.get_data()
    await state.update_data({"bill_id":callback_data.bill_id})
   
    markup = await bill_keyboards.open_bill(await Bills.get_bill(callback_data.bill_id), data.get("current_page"))

    await query.message.edit_text("Bill", reply_markup = markup)

@orders_router.callback_query(OrderNavigateCallback.filter(F.action == "close_bill"))
async def orders_close_bill(query: CallbackQuery, state: FSMContext, callback_data: OrderNavigateCallback):
    await query.answer()

    await Bills.close_bill(callback_data.bill_id)

    bill = await Bills.get_bill(callback_data.bill_id)

    for order in bill.orders:
        result = await Order.get_order(order)
        for data in result.cart:
            id, weight = list(data.items())[0]
            tabacco = await Tabacco.get_by_id(id)
            await Tabacco.update_weight(id, tabacco.weight - weight)

    
    bill_keyboards.update(data = await Bills.get_all_bills({"is_closed":False}))    

    markup = bill_keyboards.bills_list()

    logging.log(30, f"Closed bill {bill.bill_name}. Crerated by {bill.created_by}. Closed by {query.from_user.id}")
    await query.message.edit_text("Bill", reply_markup = markup)



@orders_router.callback_query(OrderNavigateCallback.filter(F.action == "add_new_order"))
async def orders_new_order(query: CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    await state.set_state(EditBill.new_order)
    await state.update_data(data)

    markup = bill_keyboards.new_order(data.get("bill_id"))

    await query.message.edit_text("New order", reply_markup = markup)


bill_keyboards.register_handler(bill_keyboards.navigate_choose_page_slider, [EditBill.new_order, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])
bill_keyboards.register_handler(bill_keyboards.navigate_page_num_keyboard, [EditBill.new_order, NumKeyboardCallback.filter(F.action.not_in(["commit"]))])
@orders_router.callback_query(EditBill.new_order, OrderNavigateCallback.filter(F.action == "hookah"))
async def orders_select_type(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data({"cart":{}})
    data = await state.get_data()

    bill_keyboards.update(data = await Tabacco.get_all())

    markup = bill_keyboards.choose_tabacco(cart = data.get("cart"), bill_id = data.get("bill_id"))

    await query.message.edit_text("New order", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, NavigatePageKeyboard.filter(F.action == "choose_tabacco"))
async def orders_choose_tabacco(query: CallbackQuery, state: FSMContext, callback_data: NavigatePageKeyboard):
    await query.answer()
    current_tabacco = await Tabacco.get_by_id(callback_data.kwargs)
    await state.update_data({"current_tabacco":current_tabacco})
    await state.update_data({"current_num":0})

    markup = bill_keyboards.show_num_keyboard()

    await query.message.edit_text("Input weight", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, OrderNavigateCallback.filter(F.action == "open_cart"))
async def orders_show_cart(query: CallbackQuery, state: FSMContext):
    await query.answer()

    data = await state.get_data()
    cart = data.get("cart")

    markup = bill_keyboards.show_cart_keyboard(cart)

    await query.message.edit_text("Cart", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, OrderNavigateCallback.filter(F.action == "remove"))
async def orders_remove_from_cart(query: CallbackQuery, state: FSMContext, callback_data: OrderNavigateCallback):
    await query.answer()

    data = await state.get_data()
    cart = data.get("cart")
    cart.pop(callback_data.bill_id)

    await state.update_data(cart)

    markup = bill_keyboards.show_cart_keyboard(cart)

    await query.message.edit_text("Cart", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, NumKeyboardCallback.filter(F.action == "commit"))
async def orders_update_choosed_tabacco(query: CallbackQuery, state: FSMContext, callback_data: NavigatePageKeyboard):
    await query.answer()

    data = await state.get_data()
    current_tabacco, current_number = data.get("current_tabacco"), data.get("current_num")
    current_tabacco.used_weight = current_number
    cart = data.get("cart")
    cart.update({current_tabacco._id.__str__():current_tabacco})
    await state.update_data(cart)

    logging.log(30, cart)

    markup = bill_keyboards.choose_tabacco(cart = cart, bill_id = data.get("bill_id"))

    await query.message.edit_text("Choose tabacco", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, OrderNavigateCallback.filter(F.action == "commit_mix"))
async def orders_commit_cart(query: CallbackQuery, state: FSMContext, callback_data: OrderNavigateCallback):
    await query.answer()

    markup = bill_keyboards.show_choose_cost()

    await query.message.edit_text("Choose price", reply_markup = markup)

@orders_router.callback_query(EditBill.new_order, OrderNavigateCallback.filter(F.action == "cost"))
async def orders_commit_cost(query: CallbackQuery, state: FSMContext, callback_data: OrderNavigateCallback):
    await query.answer()

    cost = callback_data.bill_id
    data = await state.get_data()
    cart = data.get("cart")
    bill_id = data.get("bill_id")

    order_id = await Order.create_order("test_day", query.from_user.id, [{key:value.used_weight} for key, value in cart.items()], cost)
    await Bills.update_orders(bill_id, order_id)

    markup = await bill_keyboards.open_bill(await Bills.get_bill(bill_id), data.get("current_page"))

    await query.message.edit_text("Bill", reply_markup = markup)