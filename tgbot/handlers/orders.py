import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from ..misc.cache import Cache

from ..misc.history_manager import Manager
from ..keyboards.orders import OrderKeyboards
from ..keyboards.callbacks import (
    NavigatePageKeyboard, 
    OrderNavigateCallback, 
    NumKeyboardCallback, 
)

from ..models import Order, Bills, Tabacco
from ..misc.states import NewOrder, BillStates

orders_router = Router()

order_keyboars = OrderKeyboards()
order_keyboars.connect_router(orders_router)
order_keyboars.register_handler(order_keyboars.navigate_page_slider, [NewOrder.new_hookah, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])
order_keyboars.register_handler(order_keyboars.navigate_page_num_keyboard, [NewOrder.choose_tabacco, NumKeyboardCallback.filter(F.action.not_in(["commit"]))])
order_keyboars.register_handler(order_keyboars.navigate_page_num_keyboard, [NewOrder.edit_weight, NumKeyboardCallback.filter(F.action.not_in(["commit"]))])


@orders_router.callback_query(StateFilter(BillStates.bills_list), OrderNavigateCallback.filter(F.action == "open_bill"))
async def orders_open_bill(query: CallbackQuery, cache: Cache, callback_data: OrderNavigateCallback, Manager: Manager):
    await query.answer()

    markup = await order_keyboars.open_bill(await cache.getBill(callback_data.bill_id))

    await query.message.edit_text("Bill", reply_markup = markup)

    await Manager.push(BillStates.open_bill.state, {"bill_id":callback_data.bill_id})



@orders_router.callback_query(StateFilter(BillStates.open_bill), OrderNavigateCallback.filter(F.action == "add_new_order"))
async def orders_new_order(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()

    markup = order_keyboars.new_order()
    await query.message.edit_text("New order", reply_markup = markup) #noqa

    await Manager.push(state = NewOrder.new_order.state)


@orders_router.callback_query(StateFilter(NewOrder.new_order), OrderNavigateCallback.filter(F.action == "hookah"))
async def orders_select_type(query: CallbackQuery, state: FSMContext, Manager: Manager, cache: Cache):
    await query.answer()
    cart = await Manager.get_data("cart")
    order_keyboars.update(data = await cache.getAllTabacco())

    markup = order_keyboars.choose_tabacco(cart = cart)
    await query.message.edit_text("New order", reply_markup = markup)

    await Manager.push(state = NewOrder.new_hookah.state, data={"cart":{}, "current_page":1}, push = True)
    await state.set_state(NewOrder.new_hookah)


@orders_router.callback_query(StateFilter(NewOrder.new_hookah), OrderNavigateCallback.filter(F.action == "choose_tabacco"))
async def orders_choose_tabacco(query: CallbackQuery, Manager: Manager, callback_data: OrderNavigateCallback):
    await query.answer()

    markup = order_keyboars.show_num_keyboard()
    await query.message.edit_text("Input weight", reply_markup = markup)

    current_tabacco = await Tabacco.get_by_id(callback_data.tabacco_id)
    await Manager.push(state = NewOrder.choose_tabacco.state, data = {"current_tabacco":current_tabacco.to_dict(),"current_num":0})


@orders_router.callback_query(StateFilter(NewOrder.choose_tabacco), NumKeyboardCallback.filter(F.action == "commit"))
async def orders_commit_choose_tabacco(query: CallbackQuery, Manager: Manager):
    current_tabacco = await Manager.get_data("current_tabacco")
    used_weight =  await Manager.get_data("current_num")
    if used_weight == 0:
        await query.answer(text = "Weight can't be zero", show_alert = True)
        return

    await query.answer()
    cart = await Manager.get_data("cart")
    markup = order_keyboars.choose_tabacco(cart = cart)

    await query.message.edit_text(text = "Choose tabacco", reply_markup = markup)

    data = {
        current_tabacco.get("_id"):{"used_weight": used_weight}
    }
    await Manager.push_data(NewOrder.new_hookah, data, "cart", True)
    await Manager.goto(NewOrder.new_hookah)


@orders_router.callback_query(StateFilter(NewOrder.new_hookah), OrderNavigateCallback.filter(F.action == "open_cart"))
async def orders_show_cart(query: CallbackQuery, state: FSMContext, Manager: Manager):
    await query.answer()
    cart = await Manager.get_data("cart")
    markup = await order_keyboars.show_cart_keyboard(cart)
    await query.message.edit_text("Cart", reply_markup = markup)
    
    await Manager.push(NewOrder.open_cart.state)


@orders_router.callback_query(StateFilter(NewOrder.open_cart), OrderNavigateCallback.filter(F.action == "remove"))
async def orders_remove_from_cart(query: CallbackQuery, Manager: Manager, callback_data: OrderNavigateCallback):
    await query.answer()

    cart = await Manager.get_data("cart")
    cart.pop(callback_data.tabacco_id)
    await Manager.push_data(NewOrder.new_hookah, cart, "cart")

    markup = await order_keyboars.show_cart_keyboard(cart)

    await query.message.edit_text("Cart", reply_markup = markup)

@orders_router.callback_query(StateFilter(NewOrder.open_cart), OrderNavigateCallback.filter(F.action == "edit"))
async def orders_edit_from_cart(query: CallbackQuery, Manager: Manager, callback_data: OrderNavigateCallback):
    await query.answer()
    cart = await Manager.get_data("cart", NewOrder.new_hookah)

    data = {
        "current_tabacco":callback_data.tabacco_id,
        "current_num":cart[callback_data.tabacco_id].get("used_weight")
    }
    
    await Manager.push(NewOrder.edit_weight.state, data = data)

    markup = order_keyboars.show_num_keyboard(current_num = data.get("current_num")) #noqa

    await query.message.edit_text("Input weight", reply_markup = markup) #noqa


@orders_router.callback_query(StateFilter(NewOrder.edit_weight), NumKeyboardCallback.filter(F.action == "commit"))
async def orders_commit_edit_tabacco(query: CallbackQuery, Manager: Manager):
    current_tabacco = await Manager.get_data("current_tabacco")
    used_weight =  await Manager.get_data("current_num")
    if used_weight == 0:
        await query.answer(text = "Weight can't be zero", show_alert = True)
        return

    await query.answer()

    data = {
        current_tabacco:{"used_weight": used_weight}
    }

    cart = await Manager.get_data("cart", NewOrder.new_hookah)
    cart[current_tabacco] = {"used_weight":used_weight}

    await Manager.push_data(NewOrder.new_hookah, data, "cart")
    await Manager.goto(NewOrder.open_cart)

    markup = await order_keyboars.show_cart_keyboard(cart = cart)

    await query.message.edit_text(text = "Cart", reply_markup = markup)

@orders_router.callback_query(StateFilter(NewOrder.new_hookah), OrderNavigateCallback.filter(F.action == "commit_mix"))
async def orders_commit_cart(query: CallbackQuery, Manager: Manager):
    cart = await Manager.get_data("cart")
    if not cart:
        await query.answer(text = "Cart can't be empty", show_alert = True)
        return

    await query.answer()
    await Manager.push(NewOrder.choose_cost.state)
    markup = order_keyboars.show_choose_cost()

    await query.message.edit_text("Choose price", reply_markup = markup)

@orders_router.callback_query(StateFilter(NewOrder.choose_cost), OrderNavigateCallback.filter(F.action == "cost"))
async def orders_commit_cost(query: CallbackQuery, Manager: Manager, callback_data: OrderNavigateCallback):
    await query.answer()

    cost = callback_data.cost
    cart = await Manager.get_data("cart", NewOrder.new_hookah)
    bill_id = await Manager.get_data("bill_id", BillStates.open_bill)

    order_id = await Order.create_order("Shisha", query.from_user.id, [{key:value.get("used_weight")} for key, value in cart.items()], cost)
    await Bills.update_orders(bill_id, order_id)

    await Manager.goto(BillStates.open_bill)

    markup = await order_keyboars.open_bill(await Bills.get_bill(bill_id))

    await query.message.edit_text("Bill", reply_markup = markup) #noqa



@orders_router.callback_query(StateFilter(BillStates.open_bill), OrderNavigateCallback.filter(F.action == "open_order"))
async def orders_open_order(query: CallbackQuery, Manager: Manager, callback_data: OrderNavigateCallback):
    await query.answer()
    order_id = callback_data.order_id
    await Manager.push(BillStates.edit_order.state, {"order_id":order_id})

    markup = await order_keyboars.show_order_keyboard(order_id = order_id)

    await query.message.edit_text("Edit order", reply_markup = markup)  


@orders_router.callback_query(StateFilter(BillStates.edit_order), OrderNavigateCallback.filter(F.action == "remove_order"))
async def orders_remove_order(query: CallbackQuery, Manager: Manager):
    await query.answer()
    bill_id = await Manager.get_data("bill_id", BillStates.open_bill)
    order_id = await Manager.get_data("order_id")
    await Manager.goto(BillStates.open_bill)

    await Bills.remove_order(bill_id, order_id)

    markup = await order_keyboars.open_bill(await Bills.get_bill(bill_id))
    await query.message.edit_text("Open bill", reply_markup = markup)


@orders_router.callback_query(StateFilter(BillStates.edit_order), OrderNavigateCallback.filter(F.action == "discount_order"))
async def orders_discount_order():
    pass

@orders_router.callback_query(StateFilter(BillStates.edit_order), OrderNavigateCallback.filter(F.action == "save_mix"))
async def orders_save_mix():
    pass


#back

@orders_router.callback_query(StateFilter(NewOrder, BillStates), OrderNavigateCallback.filter(F.action == "back"))
async def back(query: CallbackQuery, Manager: Manager, state: FSMContext):
    await query.answer()
    await Manager.pop()

    _state_record = await Manager.get()

    await state.set_state(_state_record.state)

    cart = await Manager.get_data("cart") if await Manager.get_data("cart") else {}
    bill_id = await Manager.get_data("bill_id") if await Manager.get_data("bill_id") else None
    markups = {
        "BillStates:open_bill":await order_keyboars.open_bill(await Bills.get_bill(bill_id)) if bill_id else None,
        "NewOrder:new_order":order_keyboars.new_order(),
        "NewOrder:new_hookah":order_keyboars.choose_tabacco(cart = cart),
        "NewOrder:open_cart":await order_keyboars.show_cart_keyboard(cart = cart)
    }

    reply_text = {
        "BillStates:open_bill":"Bill",
        "NewOrder:new_order":"New order",
        "NewOrder:new_hookah":"Choose tabacco",
        "NewOrder:open_cart":"Cart",
    }

    text = reply_text.get(_state_record.state)
    markup = markups.get(_state_record.state)
    await query.message.edit_text(text = text, reply_markup = markup)