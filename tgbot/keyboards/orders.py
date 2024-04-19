import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict, Union
from datetime import datetime

from tgbot import keyboards
from tgbot.handlers import orders

from ..misc.history_manager import Manager
from ..models import BillData, OrderData, Order, User,Tabacco

from .callbacks import BillsCommit, BillsNavigate, OrderNavigateCallback, NavigatePageKeyboard, NumKeyboardCallback, MenuNavigateCallback
from .pager import BasicPageGenerator


class OrderKeyboards(BasicPageGenerator):
    _navigate_callback = BillsNavigate
    _commit_callback = BillsCommit
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data: NavigatePageKeyboard, Manager: Manager):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        await Manager.update({"current_page":current_page})
        
        markup = self.choose_tabacco(cart = await Manager.get_data("cart"), current_page = current_page)

        await query.message.edit_text(text = "Choose tabacco: ", reply_markup = markup)

    async def open_bill(self, bill: BillData):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text = f"{bill.bill_name} | Created {(str((datetime.utcnow() - bill.timestamp)).split(', ')[-1]).split('.')[0]} ago",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))
        if bill.orders:
            for order in bill.orders:
                result = await Order.get_order(order_id = order)
                keyboard.button(text = f"{result.order_name} | {result.cost} pln",
                        callback_data = OrderNavigateCallback(action = "open_order", order_id = result._id.__str__()))
        else:
            keyboard.button(text = "(No orders)",
                        callback_data = OrderNavigateCallback(action = "static", bill_id = bill._id.__str__()))

        keyboard.button(text = "Add",
                        callback_data = OrderNavigateCallback(action = "add_new_order", bill_id = bill._id.__str__()))
        
        keyboard.adjust(1, repeat = True)
        
        operation_keyboard = InlineKeyboardBuilder()
        operation_keyboard.button(text = "Close bill",
                        callback_data = BillsNavigate(action = "close_bill"))
        operation_keyboard.button(text = "Options",
                        callback_data = OrderNavigateCallback(action = "options", bill_id = bill._id.__str__()))
        
        keyboard.row(*operation_keyboard.buttons, width = 2)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<< Bills <<", callback_data = BillsNavigate(action = "back")))
        
        return keyboard.as_markup()
    
    def new_order(self):
        keyboard = InlineKeyboardBuilder()

        menu = ["Hookah", "Other"]

        for button in menu:
            keyboard.button(text = button, callback_data = OrderNavigateCallback(action = button.lower(), bill_id = ""))

        keyboard.button(text = "<< Bill <<", callback_data = OrderNavigateCallback(action = "back"))
        keyboard.adjust(len(menu), 1)

        return keyboard.as_markup()
    
    def choose_tabacco(self, cart, current_page = 1):
        keyboard = InlineKeyboardBuilder()

        if not cart:
            cart = {}

        keyboard.button(text = f" Cart ({len(cart)})", callback_data = OrderNavigateCallback(action = "open_cart", bill_id = " "))

        start_index, end_index = self.indexes(current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(
                text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
                callback_data = OrderNavigateCallback(action = "choose_tabacco", tabacco_id=raw._id.__str__())
            )

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        commit = InlineKeyboardBuilder()
        commit.button(text = "Commit mix",callback_data = OrderNavigateCallback(action = "commit_mix"))
        keyboard.attach(commit)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Cancel <<",callback_data = OrderNavigateCallback(action = "back"))

        keyboard.attach(back_button)

        return keyboard.as_markup()

    async def navigate_page_num_keyboard(self, query: CallbackQuery, callback_data: NumKeyboardCallback, Manager: Manager):
        await query.answer()

        if callback_data.action == "clear":
            await Manager.update_data("current_num", 0)
            markup = self.show_num_keyboard(current_num=0)

        elif callback_data.action == "static":
            return
        
        else:
            operand = float(callback_data.action) if callback_data.action.find(".") else int(callback_data.action)
            current_num = await Manager.get_data("current_num")
            if (current_num + operand) <= 0:
                await Manager.update_data("current_num", 0)
                markup = self.show_num_keyboard(current_num=0)
            else:
                current_num = round(current_num + operand, 1)
                await Manager.update_data("current_num", current_num)
                markup = self.show_num_keyboard(current_num=current_num)

        await query.message.edit_text("Input invent weight", reply_markup = markup)

    def show_num_keyboard(self, current_num: Union[int, float] = 0):
        keyboard = InlineKeyboardBuilder(self.page_num_keyboard(callback = NumKeyboardCallback, current_num = current_num).inline_keyboard)

        keyboard.button(text = "Cancel", callback_data = OrderNavigateCallback(action = "back"))

        return keyboard.as_markup()
    
    async def show_cart_keyboard(self, cart):
        keyboard = InlineKeyboardBuilder()

        for key, value in cart.items():
            tabacco = await Tabacco.get_by_id(key)
            tabacco.used_weight = value.get("used_weight")
            logging.info(tabacco)
            builder = InlineKeyboardBuilder()
            builder.button(text = f"{tabacco.brand} | {tabacco.label} | Used: {tabacco.used_weight}g", callback_data = OrderNavigateCallback(action = "static", bill_id = " "))
            builder.button(text = "📝", callback_data = OrderNavigateCallback(action = "edit", tabacco_id = key))
            builder.button(text = "❌", callback_data = OrderNavigateCallback(action = "remove", tabacco_id = key))
            builder.adjust(1,2)
            keyboard.attach(builder)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<< Tabacco <<", callback_data = OrderNavigateCallback(action = "back")))

        return keyboard.as_markup()
    
    def show_choose_cost(self):
        keyboard = InlineKeyboardBuilder()

        cost_menu = [
            {"Standart":80},
            {"Premium": 100},
            {"Stuff": 40},
        ]

        for type in cost_menu:
            name, cost = list(type.items())[0]
            keyboard.button(text = name, callback_data = OrderNavigateCallback(action = "cost", cost = str(cost)))

        keyboard.adjust(2, repeat=True)

        return keyboard.as_markup()

    async def show_order_keyboard(self, order_id: str):
        keyboard = InlineKeyboardBuilder()
        order = await Order.get_order(order_id = order_id)
        user = await User.get_user_by_user_id(order.created_by)
        keyboard.button(
            text = f"{order.order_name} | Created: {(str((datetime.utcnow() - order.timestamp)).split(', ')[-1]).split('.')[0]} ago ", 
            callback_data=OrderNavigateCallback(action = "static")
        )
        keyboard.button(
            text = f"Created by: {user.username} | {user.post.name}".ljust(40), 
            callback_data=OrderNavigateCallback(action = "static")
        )
        keyboard.adjust(1, True)

        counter = 1
        for tabacco in order.cart:
            cart_keyboard = InlineKeyboardBuilder()
            tabacco_id, used_weight = list(tabacco.items())[0]
            tabacco = await Tabacco.get_by_id(tabacco_id)
            cart_keyboard.button(
                text = f"{counter}) {tabacco.brand} | {tabacco.label} --> {used_weight}g ", 
                callback_data=OrderNavigateCallback(action = "static")
            )
            keyboard.attach(cart_keyboard)
            counter += 1

        option_keyboard = InlineKeyboardBuilder()
        option_keyboard.button(
            text = "Save mix 💾",
            callback_data = OrderNavigateCallback(action = "save_mix")
        )
        option_keyboard.button(
            text = "Remove❌", 
            callback_data = OrderNavigateCallback(action = "remove_order")
        )

        option_keyboard.button(
            text = "Discount💸",
            callback_data = OrderNavigateCallback(action = "discount_order")
        )

        option_keyboard.adjust(1,2)
        keyboard.attach(option_keyboard)
        keyboard.attach(InlineKeyboardBuilder().button(text = "<<Bill<<", callback_data = OrderNavigateCallback(action="back")))

        return keyboard.as_markup()

