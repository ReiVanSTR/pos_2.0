import logging
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from ..misc.history_manager import Manager

from ..models import BillData, Order, User, Permissions
from ..misc.cache import Cache
from .callbacks import BillsCommit, BillsNavigate, OrderNavigateCallback, NavigatePageKeyboard
from .pager import BasicPageGenerator

class BillKeyboards(BasicPageGenerator):
    _navigate_callback = BillsNavigate

    def bills_commit(self, callback = BillsCommit):
        keyboard = InlineKeyboardBuilder()

        keyboard.button(
            text = "Tak",
            callback_data = self._navigate_callback(action = "yes")
        )

        keyboard.button(
            text = "Nie",
            callback_data = self._navigate_callback(action = "back")
        )
        keyboard.adjust(1,1)
        return keyboard.as_markup()
    
    
    
    def new_bill_cancel(self):
        keyboard = InlineKeyboardBuilder()

        keyboard.button(text = "Anuluj", callback_data = self._navigate_callback(action = "back"))

        return keyboard.as_markup()

    async def bills_menu(self, current_page = 1):
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        keyboard.button(text = " >> Nowy rachunek << ", callback_data = BillsNavigate(action = "new_bill"))

        for raw in buttons:
            user = await User.get_user_by_user_id(raw.created_by)
            keyboard.button(text = f"{raw.bill_name} | {user.username} | {raw.timestamp.strftime('%d-%m %H:%M')}", callback_data = OrderNavigateCallback(action = "open_bill", bill_id=raw._id.__str__()))

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Rachunki <<", callback_data = BillsNavigate(action = "back"))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data: NavigatePageKeyboard, Manager: Manager, cache: Cache):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        await Manager.update({"current_page":current_page})
        
        markup = await self.bills_menu(current_page = current_page)

        await query.message.edit_text(text = "Rachunki: ", reply_markup = markup)

    async def open_bill(self, bill: BillData):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text = f"{bill.bill_name} | Otwarty {(str((datetime.utcnow() - bill.timestamp)).split(', ')[-1]).split('.')[0]} temu",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))
        if bill.orders:
            for order in bill.orders:
                result = await Order.get_order(order_id = order)
                keyboard.button(text = f"{result.order_name} | {result.cost} pln",
                        callback_data = OrderNavigateCallback(action = "open_order", order_id = result._id.__str__()))
        else:
            keyboard.button(text = "(Brak zamówień)",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))

        keyboard.button(text = "Dodaj",
                        callback_data = OrderNavigateCallback(action = "add_new_order", bill_id = bill._id.__str__()))
        
        keyboard.adjust(1, repeat = True)
        
        operation_keyboard = InlineKeyboardBuilder()
        operation_keyboard.button(text = "Zamknij rachunek",
                        callback_data = BillsNavigate(action = "close_bill"))
        operation_keyboard.button(text = "Opcje",
                        callback_data = BillsNavigate(action = "options", bill_id = bill._id.__str__()))
        
        keyboard.row(*operation_keyboard.buttons, width = 2)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<< Rachunki <<", callback_data = BillsNavigate(action = "back")))
        
        return keyboard.as_markup()
    
    def show_paymant_keyboard(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text = "Karta", callback_data=BillsNavigate(action = "card")
        )
        keyboard.button(
            text = "Gotówka", callback_data=BillsNavigate(action = "cash")
        )
        keyboard.button(
            text = "RW (Chief)", callback_data=BillsNavigate(action = "chief")
        )
        
        keyboard.adjust(2,1)
        keyboard.attach(InlineKeyboardBuilder().button(text = "Anuluj", callback_data = BillsNavigate(action = "back")))

        return keyboard.as_markup()
    
    def show_options(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text = "Usuń", callback_data = BillsNavigate(action = "delete_bill", permissions = Permissions.BILLS_REMOVE_BILL.value)
        )
        keyboard.button(
            text = "Przekaż rachunek", callback_data = BillsNavigate(action = "hand_over_bill")
        )
        keyboard.attach(InlineKeyboardBuilder().button(text = "Anuluj", callback_data = BillsNavigate(action = "back")))
        return keyboard.as_markup()