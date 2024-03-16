import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict
from datetime import datetime

from tgbot import keyboards
from tgbot.handlers import orders


from ..models import BillData, OrderData, Order

from .callbacks import BillsCommit, BillsNavigateCallback, OrderNavigateCallback, NavigatePageKeyboard, NumKeyboardCallback
from .pager import BasicPageGenerator


class BillKeyboards(BasicPageGenerator):
    _navigate_callback = BillsNavigateCallback
    _commit_callback = BillsCommit

    def bills_commit(self, callback = BillsCommit):
        keyboard = InlineKeyboardBuilder()

        keyboard.button(
            text = "Yes",
            callback_data = callback(commit = "yes")
        )

        keyboard.button(
            text = "Nope",
            callback_data = callback(commit = "no")
        )
        keyboard.adjust(1,1)
        return keyboard.as_markup()

    def bills_menu(self):
        menu = ["New bill", "Bills"]
        keyboard = InlineKeyboardBuilder()

        for menu_button in menu:
            keyboard.button(
                text = menu_button,
                callback_data = self._navigate_callback(button_name = menu_button.replace(" ", "_").lower(), type = "category")
            )

        return keyboard.as_markup()

    def bills_list(self, current_page = 1):
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(text = f"{raw.bill_name} | {raw.created_by} | {raw.timestamp.strftime('%d-%m %H:%M')}", callback_data = OrderNavigateCallback(action = "open_bill", bill_id=raw._id.__str__()))

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Bills menu <<", callback_data = BillsNavigateCallback(button_name = "main", type = "category"))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data: NavigatePageKeyboard, state: FSMContext):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        await state.set_data({"current_page":current_page})
        
        markup = self.bills_list(current_page = current_page)

        await query.message.edit_text(text = "Bills: ", reply_markup = markup)

    async def open_bill(self, bill: BillData, current_page):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text = f"{bill.bill_name} | Created {(str((datetime.utcnow() - bill.timestamp)).split(', ')[-1]).split('.')[0]} ago",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))
        if bill.orders:
            for order in bill.orders:
                result = await Order.get_order(order_id = order)
                keyboard.button(text = f"{result.order_name} | {result.cost}",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))
        else:
            keyboard.button(text = "(Nothing)",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))

        keyboard.button(text = "Add",
                        callback_data = OrderNavigateCallback(action = "add_new_order", bill_id = bill._id.__str__()))
        
        keyboard.adjust(1, repeat = True)
        
        operation_keyboard = InlineKeyboardBuilder()
        operation_keyboard.button(text = "Close bill",
                        callback_data = OrderNavigateCallback(action = "close_bill", bill_id = bill._id.__str__()))
        operation_keyboard.button(text = "Options",
                        callback_data = OrderNavigateCallback(action = "options", bill_id = bill._id.__str__()))
        
        keyboard.row(*operation_keyboard.buttons, width = 2)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<< Bills <<", callback_data = NavigatePageKeyboard(action = "redraw", current_page = current_page)))
        
        return keyboard.as_markup()
    
    def new_order(self, bill_id):
        keyboard = InlineKeyboardBuilder()

        menu = ["Hookah", "Other"]

        for button in menu:
            keyboard.button(text = button, callback_data = OrderNavigateCallback(action = button.lower(), bill_id = ""))

        keyboard.button(text = "<< Bill <<", callback_data = OrderNavigateCallback(action = "open_bill", bill_id = bill_id))
        keyboard.adjust(len(menu), 1)

        return keyboard.as_markup()
    
    def choose_tabacco(self, cart, bill_id, current_page = 1):
        keyboard = InlineKeyboardBuilder()

        keyboard.button(text = f" Cart ({len(cart)})", callback_data = OrderNavigateCallback(action = "open_cart", bill_id = " "))

        start_index, end_index = self.indexes(current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(
                text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
                callback_data = NavigatePageKeyboard(action = "choose_tabacco", current_page = current_page, kwargs=raw._id.__str__())
            )

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        commit = InlineKeyboardBuilder()
        commit.button(text = "Commit mix",callback_data = OrderNavigateCallback(action = "commit_mix", bill_id = bill_id))
        keyboard.attach(commit)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Cancel <<",callback_data = OrderNavigateCallback(action = "open_bill", bill_id = bill_id))

        keyboard.attach(back_button)

        return keyboard.as_markup()

    async def navigate_choose_page_slider(self, query: CallbackQuery, callback_data: NavigatePageKeyboard, state: FSMContext):
        await query.answer()
        data = await state.get_data()
        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        # await state.set_data({"current_page":current_page})
        
        markup = self.choose_tabacco(cart = data.get("cart"), bill_id = data.get("bill_id"), current_page = current_page)

        await query.message.edit_text(text = "Choose tabacco: ", reply_markup = markup)

    async def navigate_page_num_keyboard(self, query: CallbackQuery, callback_data: NumKeyboardCallback, state: FSMContext):
        await query.answer()

        state_data = await state.get_data()
        await state.update_data({"current_num":state_data["current_num"]})

        if callback_data.action == "clear":
            await state.update_data({"current_num":0})
            markup = self.show_num_keyboard(current_num=0)
        elif callback_data.action == "static":
            return
        elif callback_data.action == "commit":
            await state.update_data({"current_num":state_data["current_num"]})
            return 
        else:
            operand = float(callback_data.action) if callback_data.action.find(".") else int(callback_data.action)
            current_num = state_data["current_num"]
            if (current_num + operand) <= 0:
                await state.update_data({"current_num":0})
                markup = self.show_num_keyboard(current_num=0)
            else:
                current_num = round(current_num + operand, 1)
                await state.update_data({"current_num":current_num})
                markup = self.show_num_keyboard(current_num=current_num)

        await query.message.edit_text("Input invent weight", reply_markup = markup)

    def show_num_keyboard(self, current_num = 0):
        keyboard = InlineKeyboardBuilder(self.page_num_keyboard(callback = NumKeyboardCallback, current_num = current_num).inline_keyboard)

        keyboard.button(text = "Cancel", callback_data = NavigatePageKeyboard(action = "redraw", current_page = 1))

        return keyboard.as_markup()
    
    def show_cart_keyboard(self, cart):
        keyboard = InlineKeyboardBuilder()

        for key, tabacco in cart.items():
            builder = InlineKeyboardBuilder()
            builder.button(text = f"{tabacco.brand} | {tabacco.label} | Used: {tabacco.used_weight}g", callback_data = OrderNavigateCallback(action = "static", bill_id = " "))
            builder.button(text = "📝", callback_data = OrderNavigateCallback(action = "edit", bill_id = key))
            builder.button(text = "❌", callback_data = OrderNavigateCallback(action = "remove", bill_id = key))
            builder.adjust(1,2)
            keyboard.attach(builder)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<< Tabacco <<", callback_data = NavigatePageKeyboard(action = "redraw", current_page = 1)))

        return keyboard.as_markup()
    
    def show_choose_cost(self):
        keyboard = InlineKeyboardBuilder()

        menu = ["80", "100", "64", "80", "40"]

        for button in menu:
            keyboard.button(text = button, callback_data = OrderNavigateCallback(action = "cost", bill_id = button))

        keyboard.adjust(2, repeat=True)

        return keyboard.as_markup()