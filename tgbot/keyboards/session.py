from typing import Dict, Any, Union
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery

from ..misc.history_manager import Manager
from ..keyboards.callbacks import SessionNavigateCallback, NavigatePageKeyboard
from ..keyboards.pager import BasicPageGenerator
from ..enums.keyboards.session_keyboard import ButtonActions
from ..models import SessionData, Session, ObjectId, Bills, BillData, User, UserData, Order
from .tools import get_timedelta


class SessionKeyboards(BasicPageGenerator):

    def open_session():
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text = "Open session",
            callback_data = SessionNavigateCallback(action = ButtonActions.OPEN_SESSION.value)
        )
        keyboard.button(
            text = "<<",
            callback_data = SessionNavigateCallback(action = ButtonActions.BACK.value)
        )
        keyboard.adjust(1, repeat = True)
        return keyboard.as_markup()

    async def session_menu(self, session_data: SessionData):
        keyboard = InlineKeyboardBuilder()
        session_statistics: Dict[str, Any] = await Session.count_total()
        if not session_statistics:
            session_statistics = {}

        keyboard.button(
            text = f"Session active: {get_timedelta(session_data.start_time)}",
            callback_data = SessionNavigateCallback(action = ButtonActions.STATIC.value)
        )

        keyboard.button(
            text = f"Orders count: {session_statistics.get('total_order', 0)} | Total: {session_statistics.get('total_cost', 0)} pln",
            callback_data = SessionNavigateCallback(action = ButtonActions.STATIC.value)
        )

        keyboard.button(
            text = "Last activities",
            callback_data = SessionNavigateCallback(action = ButtonActions.ACTIVITIES.value)
        )

        keyboard.button(
            text = "Close session",
            callback_data = SessionNavigateCallback(action = ButtonActions.CLOSE_SESSION.value)
        )

        keyboard.button(
            text = "<<",
            callback_data = SessionNavigateCallback(action = ButtonActions.BACK.value)
        )
        keyboard.adjust(1, repeat = True)
        return keyboard.as_markup()
    
    async def session_activities(self, current_page = 1):
        # activities_list = await Session.get_activities()
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        for activity in buttons:
            _keyboard = InlineKeyboardBuilder()
            _keyboard.button(
                text = f"{activity['bill_name']} | {activity['created_by'][0]['username']}",
                callback_data = SessionNavigateCallback(action = ButtonActions.OPEN_BILL.value, bill_id = activity["_id"].__str__())
            )

            _keyboard.adjust(2)
            keyboard.attach(_keyboard)

        navigate_buttons = self.slide_page(current_page)
        keyboard.row(*navigate_buttons.buttons, width = 5)

        keyboard.attach(InlineKeyboardBuilder().button(
            text = "<<",
            callback_data = SessionNavigateCallback(action = ButtonActions.BACK.value)
        ))

        return keyboard.as_markup()
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data: NavigatePageKeyboard, Manager: Manager):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        await Manager.update({"current_page":current_page})
        
        markup = await self.session_activities(current_page = current_page)

        await query.message.edit_text(text = "Session activities: ", reply_markup = markup)


    async def session_edit_bill(self, bill_id: str):
        bill: BillData = await Bills.get_bill(bill_id)
        user: UserData = await User.get_user_by_user_id(bill.created_by)

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text = f"{bill.bill_name} | {user.username} | Created {get_timedelta(bill.timestamp)} ago",
                        callback_data = SessionNavigateCallback(action = ButtonActions.STATIC.value)
        )
        if bill.orders:
            for order in bill.orders:
                result = await Order.get_order(order_id = order)
                keyboard.button(text = f"{result.order_name} | {result.cost} pln",
                        callback_data = SessionNavigateCallback(action = ButtonActions.OPEN_ORDER.value, order_id = result._id.__str__()))
        else:
            keyboard.button(text = "(No orders)",
                        callback_data = SessionNavigateCallback(action = ButtonActions.STATIC.value))

        keyboard.adjust(1, repeat = True)
        
        operation_keyboard = InlineKeyboardBuilder()
        operation_keyboard.button(text = "Open bill",
                        callback_data = SessionNavigateCallback(action = ButtonActions.OPEN_BILL.value, bill_id = bill._id.__str__()))
        
        operation_keyboard.button(text = f"{bill.payment_method}",
                        callback_data = SessionNavigateCallback(action = ButtonActions.CHANGE_PAYMENT_METHOD.value, bill_id = bill._id.__str__())
                        )
        
        keyboard.row(*operation_keyboard.buttons, width = 2)


        keyboard.attach(InlineKeyboardBuilder().button(
            text = "<<",
            callback_data = SessionNavigateCallback(action = ButtonActions.BACK.value)
        ))

        return keyboard.as_markup()
        

