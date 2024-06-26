import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from .markup import onState, Markups, StateKeyboard

from ..keyboards.callbacks import MenuNavigateCallback, SessionNavigateCallback, NavigatePageKeyboard
from ..keyboards.session import SessionKeyboards
from ..keyboards.menu import MenuKeyboards
from ..models.user import UserData
from ..models import SessionData, Session, Bills, Order, Tabacco, Shift, User
from ..misc.history_manager import Manager
from ..misc.cache import Cache
from ..misc.states import SessionStates, MenuStates
from ..enums.keyboards.session_keyboard import ButtonActions
import pytz


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

    date_object = datetime.now()

    session_id = await Session.find_session_by_date(date_object)
    session = await Session.get_current_session()

    if session_id:
        logger.filelog(query.from_user.id, "Opened session", {"date":date_object}) 
        await Session.open_session_by_id(session_id = session_id)
        session = await Session.get_current_session()
        markup = await keyboard.session_menu(session)

        return await query.message.edit_text("Session", reply_markup = markup)


    session = await Session.open_session(query.from_user.id)
    logger.filelog(query.from_user.id, "Opened session")
    markup = await keyboard.session_menu(session)
    
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

    markup = await keyboard.session_open_bill(callback_data.bill_id)
    await query.message.edit_text("Edit bill", reply_markup = markup)

@session_router.callback_query(StateFilter(SessionStates.bill_options), SessionNavigateCallback.filter(F.action == ButtonActions.OPEN_ORDER.value))
async def session_open_order(query: CallbackQuery, Manager: Manager, callback_data = SessionNavigateCallback):
    await query.answer()
    await Manager.push(SessionStates.open_order, push = True)

    order_id = callback_data.order_id
    markup = await keyboard.session_show_order(order_id)
    await query.message.edit_text("Order (Can't be edited!)", reply_markup = markup)


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
    await query.answer()
    # await Manager.push(SessionStates.change_payment_method)

@session_router.callback_query(StateFilter(SessionStates.menu), SessionNavigateCallback.filter(F.action == ButtonActions.CLOSE_SESSION.value))
async def session_close_session(query: CallbackQuery, Manager: Manager, session: SessionData):
    await query.answer()
    await Manager.push(SessionStates.close_session_commit)

    markup = await keyboard.close_session_commit(session_data = session)

    await query.message.edit_text("Close session commit", reply_markup = markup)


@session_router.callback_query(StateFilter(SessionStates.close_session_commit), SessionNavigateCallback.filter(F.action == ButtonActions.CLOSE_SESSION_COMMIT.value))
async def session_commit_close_session(query: CallbackQuery, Manager: Manager, user: UserData, logger):
    date_object = datetime.now(tz = pytz.utc)

    _opened_shifts = await Shift.find_opened_shifts()
    _opened_bills = await Session.count_documents()

    if _opened_shifts:
        await query.answer(text = "Shifts not closed!", show_alert = True)
        return
    
    if _opened_bills:
        await query.answer(text = f"Close all bills! Opened: {_opened_bills}", show_alert = True)
        return

    await query.answer()
    await Manager.goto(MenuStates.menu)
    await Session.close_current_session(user.user_id)
    logger.filelog(query.from_user.id, "Closed session", {"date":date_object.isoformat()}) 

    markup = await MenuKeyboards().menu_keyboard(user)

    await query.message.edit_text(f"Hello, {user.username}", reply_markup = markup)








@session_router.callback_query(SessionNavigateCallback.filter(F.action == ButtonActions.BACK.value))
async def session_back(query: CallbackQuery, Manager: Manager, user: UserData, state: FSMContext):
    await query.answer()
    await Manager.pop()
    _state_record = await Manager.get()
    await state.set_state(_state_record.state)

    markups = Markups()
    
    async def _menu_getter():
        logging.log(30, user)
        return user

    async def _on_activities():
        keyboard.update(data = await Session.get_activities())

    async def _session_activities_getter():
        return await Manager.get_data(key = "current_page")

    async def _session_menu_getter():
        return await Session.get_current_session()
    
    async def _session_open_bill_getter():
        return await Manager.get_data(key = "bill_id")

    markups.register("Menu",
        StateKeyboard(
            filtr = onState("MenuStates:menu"), 
            text = "Menu", 
            keyboard = MenuKeyboards().menu_keyboard, 
            getter = _menu_getter
        )
    )

    markups.register("SessionMenu",
        StateKeyboard(
            filtr = onState("SessionStates:menu"), 
            text = "Session", 
            keyboard = keyboard.session_menu, 
            getter = _session_menu_getter
        )
    )

    markups.register("SessionActivities",
        StateKeyboard(
            filtr = onState("SessionStates:activities"), 
            text = "Session activities", 
            keyboard = keyboard.session_activities, 
            getter = _session_activities_getter,
            on_call = _on_activities
        )
    )
    
    markups.register("SessionBillOptions",
            StateKeyboard(
                filtr = onState("SessionStates:bill_options"), 
                text = "Edit bill", 
                keyboard = keyboard.session_open_bill, 
                getter = _session_open_bill_getter
            )
        )

    result = await markups.get_markup(_state_record.state)
    await query.message.edit_text(text = result["text"], reply_markup = result["keyboard"])