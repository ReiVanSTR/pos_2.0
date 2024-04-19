import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from ..misc.history_manager import Manager

from ..misc.states import BillStates, MenuStates, FormNewBill
from ..keyboards.pager import NavigatePageKeyboard
from ..keyboards.callbacks import BillsNavigate, MenuNavigateCallback
from ..keyboards.bills import BillKeyboards
from ..keyboards.menu import MenuKeyboards
from ..models import (
    UserData,
    Bills,
    Order,
    Tabacco
)


bills_router = Router()
keyboards = BillKeyboards()
keyboards.connect_router(bills_router)
keyboards.register_handler(keyboards.navigate_page_slider, [BillStates.bills_list, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])

@bills_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "bills"))
async def show_bills_menu(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()
    await state.set_state(BillStates.bills_menu)
    await Manager.push(BillStates.bills_menu.state, {})


    markup = keyboards.bills_menu()
    await query.message.edit_text("Test", reply_markup = markup)

@bills_router.callback_query(StateFilter(BillStates.bills_menu), BillsNavigate.filter(F.action == "bills_list"))
async def show_bills_list(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()
    await Manager.push(BillStates.bills_list.state, {"current_page":1})
    await state.set_state(BillStates.bills_list)

    keyboards.update(data = await Bills.get_all_bills({"is_closed":False}))
    markup = await keyboards.bills_list()

    await query.message.edit_text("Bills list", reply_markup = markup)

@bills_router.callback_query(StateFilter(BillStates.bills_menu), BillsNavigate.filter(F.action == "new_bill"))
async def form_new_bill(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()
    await state.set_state(FormNewBill.input_name)
    await Manager.push(FormNewBill.input_name.state, {})

    markup = keyboards.new_bill_cancel()
    await query.message.edit_text("Input bill name:", reply_markup = markup)

@bills_router.message(StateFilter(FormNewBill.input_name), F.text.is_not(None))
async def form_input_name(message: Message, state: FSMContext, Manager: Manager):
    await state.set_state(FormNewBill.confirm)
    await Manager.push(FormNewBill.confirm.state, {"bill_name": message.text.strip()})

    markup = keyboards.bills_commit()


    await message.answer("Confirm", reply_markup = markup)


@bills_router.callback_query(StateFilter(FormNewBill.confirm), BillsNavigate.filter(F.action == "yes"))
async def form_commit_name(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()

    bill_name = await Manager.get_data("bill_name")
    bill_id = await Bills.create_bill(bill_name = bill_name, user_id = query.from_user.id)
    await Manager.goto(BillStates.bills_menu)
    await Manager.push(BillStates.bills_list.state, {"current_page":1})
    await Manager.push(BillStates.open_bill.state, {"bill_id":bill_id.__str__()})

    keyboards.update(data = await Bills.get_all_bills({"is_closed":False}))
    markup = await keyboards.open_bill(await Bills.get_bill(bill_id))

    await query.message.edit_text("Bills menu", reply_markup = markup)

@bills_router.callback_query(StateFilter(BillStates.open_bill), BillsNavigate.filter(F.action == "close_bill"))
async def orders_choose_payment_method(query: CallbackQuery, Manager: Manager):
    bill = await Bills.get_bill(await Manager.get_data("bill_id"))
    if not bill.orders:
        await query.answer(text = "You can't close empty bill", show_alert = True)
        return
    
    await query.answer()
    await Manager.push(BillStates.close_bill.state)

    markup = keyboards.show_paymant_keyboard()
    
    await query.message.edit_text(text = "Choose payment method", reply_markup = markup)
# 
@bills_router.callback_query(StateFilter(BillStates.close_bill), BillsNavigate.filter(F.action.in_(["card", "cash", "chief"])))
async def orders_close_bill(query: CallbackQuery, Manager: Manager, callback_data: BillsNavigate):
    await query.answer()
    bill_id = await Manager.get_data("bill_id", BillStates.open_bill)
    payment_method = callback_data.action
    await Bills.close_bill(bill_id, payment_method)

    bill = await Bills.get_bill(bill_id)

    for order in bill.orders:
        result = await Order.get_order(order)
        for data in result.cart:
            id, weight = list(data.items())[0]
            tabacco = await Tabacco.get_by_id(id)
            await Tabacco.update_weight(id, tabacco.weight - weight)

    await Manager.goto(BillStates.bills_list)

    keyboards.update(data = await Bills.get_all_bills({"is_closed":False}))    

    markup = await keyboards.bills_list()

    logging.log(30, f"Closed bill {bill.bill_name}. Crerated by {bill.created_by}. Closed by {query.from_user.id}")
    await query.message.edit_text("Bill", reply_markup = markup)


#back
@bills_router.callback_query(BillsNavigate.filter(F.action == "back"))
async def back_to_menu(query: CallbackQuery, state: FSMContext, user: UserData, Manager: Manager):
    await query.answer()
    await Manager.pop()

    _state_record = await Manager.get()

    await state.set_state(_state_record.state)
    bill_id = await Manager.get_data("bill_id")

    markups = {
        "MenuStates:menu":await MenuKeyboards().menu_keyboard(user = user),
        "BillStates:bills_menu":keyboards.bills_menu(),
        "BillStates:bills_list":await keyboards.bills_list(),
        "FormNewBill:input_name":keyboards.new_bill_cancel(),
        "BillStates:open_bill":await keyboards.open_bill(await Bills.get_bill(bill_id)) if bill_id else None
    }

    reply_text = {
        "MenuStates:menu":"Menu",
        "BillStates:bills_menu":"Bills menu",
        "BillStates:bills_list":"Bills list",
        "BillStates:open_bill":"Bill",
        "FormNewBill:input_name":"Input table name",
    }

    text = reply_text.get(_state_record.state)
    markup = markups.get(_state_record.state)
    await query.message.edit_text(text = text, reply_markup = markup) 