import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.callbacks import MenuNavigateCallback, SessionNavigateCallback, NavigatePageKeyboard
from ..keyboards.session import SessionKeyboards
from ..keyboards.menu import MenuKeyboards
from ..models.user import UserData
from ..models import SessionData, Session, Bills, Order, Tabacco
from ..misc.history_manager import Manager
from ..misc.cache import Cache
from ..misc.states import SessionStates, MenuStates
from ..enums.keyboards.session_keyboard import ButtonActions


session_router = Router()
keyboard = SessionKeyboards()
keyboard.connect_router(session_router)
keyboard.register_handler(keyboard.navigate_page_slider, [SessionStates.activities, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])

@session_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "session"))
async def session_menu(query: CallbackQuery, Manager: Manager, session: SessionData = None):
    await Manager.push(SessionStates.menu)

    if not session:
        markup = SessionKeyboards.open_session()
    else:
        markup = await keyboard.session_menu(session)

    await query.message.edit_text("Session",  reply_markup = markup)


@session_router.callback_query(StateFilter(SessionStates.menu), SessionNavigateCallback.filter(F.action == ButtonActions.OPEN_SESSION.value))
async def open_session(query: CallbackQuery, Manager: Manager, logger):
    await query.answer(text = "Session is opened")
    await Session.open_session(query.from_user.id)
    logger.filelog(query.from_user.id, "Opened session")
    
    _current_session = await Session.get_current_session()
    markup = await keyboard.session_menu(_current_session)
    await query.message.edit_text("Session", reply_markup = markup)

    
@session_router.callback_query(StateFilter(SessionStates.menu), SessionNavigateCallback.filter(F.action == ButtonActions.ACTIVITIES.value))
async def session_activities(query: CallbackQuery, Manager: Manager, logger, session: SessionData):
    await query.answer()
    await Manager.push(SessionStates.activities, {"current_page":1})

    keyboard.update(data = await Session.get_activities())
    markup = await keyboard.session_activities(1)
    await query.message.edit_text("Session activities", reply_markup = markup)

@session_router.callback_query(StateFilter(SessionStates.activities), SessionNavigateCallback.filter(F.action == ButtonActions.OPEN_BILL.value))
async def session_bill_options(query: CallbackQuery, Manager: Manager, callback_data = SessionNavigateCallback):
    await query.answer()
    await Manager.push(SessionStates.bill_options, {"bill_id":callback_data.bill_id})

    markup = await keyboard.session_edit_bill(callback_data.bill_id)
    await query.message.edit_text("Edit bill", reply_markup = markup)

@session_router.callback_query(StateFilter(SessionStates.bill_options), SessionNavigateCallback.filter(F.action == ButtonActions.OPEN_ORDER.value))
async def session_open_order(query: CallbackQuery, Manager: Manager, callback_data = SessionNavigateCallback):
    await query.answer()
    await Manager.push(SessionStates.open_order)

    order_id = callback_data.order_id
    markup = 

@session_router.callback_query(StateFilter(SessionStates.bill_options), SessionNavigateCallback.filter(F.action == ButtonActions.OPEN_BILL.value))
async def session_open_bill(query: CallbackQuery, Manager: Manager):
    await query.answer()
    bill_id = await Manager.get_data("bill_id")
    await Bills.open_bill(bill_id)

    bill = await Bills.get_bill(bill_id)

    for order in bill.orders:
        result = await Order.get_order(order)
        for data in result.cart:
            id, weight = list(data.items())[0]
            tabacco = await Tabacco.get_by_id(id)
            await Tabacco.update_weight(id, tabacco.weight + weight)

    await Manager.goto(SessionStates.activities)
    current_page = await Manager.get_data("current_page")
    keyboard.update(await Session.get_activities())
    markup = await keyboard.session_activities(current_page)

    await query.message.edit_text("Session activities", reply_markup = markup)


@session_router.callback_query(StateFilter(SessionStates.bill_options), SessionNavigateCallback.filter(F.action == ButtonActions.CHANGE_PAYMENT_METHOD.value))
async def session_change_payment_method(query: CallbackQuery, Manager: Manager):
    await Manager.push(SessionStates.change_payment_method)

@session_router.callback_query(SessionNavigateCallback.filter(F.action == ButtonActions.BACK.value))
async def session_back(query: CallbackQuery, Manager: Manager, user: UserData, state: FSMContext, session):
    await query.answer()
    await Manager.pop()
    _state_record = await Manager.get()
    # bill_id = _state_record.data.get("bill_id", None)

    await state.set_state(_state_record.state)

    keyboard.update(data = await Session.get_activities())
    

    markups = {
        "MenuStates:menu":await MenuKeyboards().menu_keyboard(user = user),
        "SessionStates:menu":await keyboard.session_menu(session),
        "SessionStates:activities":await keyboard.session_activities(),
        # "SessionStates:bill_options":await keyboard.session_edit_bill(bill_id)
    }

    reply_text = {
        "MenuStates:menu":"Menu",
        "SessionStates:menu":"Session",
        "SessionStates:activities":"Session activities",
        # "SessionStates:bill_options":"Edit bill"
    }

    text = reply_text.get(_state_record.state)
    markup = markups.get(_state_record.state)
    await query.message.edit_text(text = text, reply_markup = markup) 