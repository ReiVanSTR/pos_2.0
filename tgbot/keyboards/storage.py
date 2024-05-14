import logging
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict

from ..models import Tabacco, TabaccoData, Invent, InventData
from .pager import BasicPageGenerator
from ..misc.history_manager import Manager
from ..misc.main_query import main_query
menu = ["Add", "Invent", "Show"]

brand_types = ["Standart", "Premium", "Mix", "Pasta", "Węgiel"]

class StorageNavigate(CallbackData, prefix = "storage"):
    action: str

#add form Callback class
class Insert(CallbackData, prefix = "insert"):
    brand_type: Optional[str] = None
    brand_name: Optional[str] = None
    tabacco_name: Optional[str] = None
    commit: Optional[str] = None

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    tabacco_id: Optional[str] = ""

class StorageCommit(CallbackData, prefix = "storage_commit"):
    commit: str #yes, nope

def storage_menu():
    keyboard = InlineKeyboardBuilder()

    for menu_button in menu:
        keyboard.button(
            text = menu_button,
            callback_data = StorageNavigate(action = menu_button.lower())
        )
    
    back_button = InlineKeyboardBuilder().button(text = "<<Menu<<", callback_data = StorageNavigate(action = "back"))
    
    keyboard.attach(back_button)

    return keyboard.as_markup()

def storage_brand_types():
    keyboard = InlineKeyboardBuilder()

    for brand in brand_types:
        keyboard.button(
            text = brand,
            callback_data = Insert(brand_type = brand)
        )

    keyboard.button(
        text = "<<",
        callback_data = StorageNavigate(action = "back")
    )

    keyboard.adjust(len(brand_types), 1)

    return keyboard.as_markup()

async def storage_brand(type: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    brands = await Tabacco.get_all_brands_by_type(type)

    keyboard.button(
        text = "New brand",
        callback_data = StorageNavigate(action = "new_brand")
    )

    for brand in brands:
        keyboard.button(
            text = brand,
            callback_data = Insert(brand_name = brand)
        )

    keyboard.attach(InlineKeyboardBuilder().button(
        text = "<<",
        callback_data = StorageNavigate(action = "back")
    ))

    keyboard.adjust(1,3)
    return keyboard.as_markup()

def storage_cancel():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text = "Cancel",
        callback_data = StorageNavigate(action = "back")
    )

    return keyboard.as_markup()

def storage_commit(callback):
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



class ShowPageGenerator(BasicPageGenerator):
    # def __init__(self, data: List[TabaccoData] = []) -> None:
    #     self.data = data
    #     self.buttons_per_page = 6
    #     self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil

    # def update(self, data):
    #     logging.log(30, "updated")
    #     self.data = data
    #     self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil

        
    def show_page_keyboard(self, current_page: int = 1):
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(
                text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
                callback_data = NavigatePageKeyboard(action = "show_tabacco", current_page = current_page, tabacco_id=raw._id.__str__())
            )

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Storage <<",callback_data = StorageNavigate(action = "back"))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def tabacco_history_keyboard(self, tabacco_id: str, current_page):
        keyboard = InlineKeyboardBuilder()
        data = await Invent.get_changes(tabacco_id)
        tabacco = await Tabacco.get_by_id(tabacco_id)

        if not data:
            keyboard.button(text = "Not inventarizet yet.", callback_data = NavigatePageKeyboard(action = "static", current_page = current_page))
        else:
            for change in data.changes:
                keyboard.button(
                    text = f"Id - {change._id} | Inspector: {change.user_id} ({change.expected_weight} -> {change.accepted_weight})", 
                    callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
                )
            
            keyboard.adjust(1, repeat = True)

        remove_keyboard = InlineKeyboardBuilder()

        remove_keyboard.button(text = "Remove tabacco", callback_data = StorageNavigate(action = "remove_tabacco"))
        remove_keyboard.button(text = "Showed" if tabacco.is_showed else "Hiden", callback_data = StorageNavigate(action = "show_checkbox"))

        keyboard.attach(remove_keyboard)

        keyboard.attach(InlineKeyboardBuilder().button(text = "<<", callback_data = StorageNavigate(action = "back")))

        return keyboard.as_markup()
    
    async def navigate_callbacks(self, query: CallbackQuery, callback_data: NavigatePageKeyboard):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        markup = self.show_page_keyboard(current_page = current_page)

        await query.message.edit_text(text = "Storage", reply_markup = markup)

        

def storage_invent_menu():
    keyboard = InlineKeyboardBuilder()

    #in config
    invent_menu_buttons = ["Single", "Total"]

    for button in invent_menu_buttons:
        keyboard.button(text = button, callback_data = StorageNavigate(action = button.lower()))

    keyboard.button(text = "<<", callback_data = StorageNavigate(action = "back"))

    keyboard.adjust(1, repeat = True)

    return keyboard.as_markup()



class NumKeyboardCallback(CallbackData, prefix = "num_keyboard"):
    action: str

class InventPageGenerator(BasicPageGenerator):
    def invent_page_keyboard(self, current_page: int = 1):
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(
                text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
                callback_data = NavigatePageKeyboard(action = "select_button", current_page = current_page, tabacco_id = raw._id.__str__())
            )

        keyboard.adjust(1, repeat = True)

        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)
        
        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Invent <<",callback_data = StorageNavigate(action = "back"))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data = NavigatePageKeyboard):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        markup = self.invent_page_keyboard(current_page = current_page)

        await query.message.edit_text(text = "Invent", reply_markup = markup)

    async def massage_input(self, message: Message, Manager: Manager, user):
        try:
            if isinstance(float(message.text.strip()), float):
                await Manager.update_data("current_num", float(message.text.strip()))
                markup = self.show_num_keyboard(current_num=float(message.text.strip()))
        except:
            markup = self.show_num_keyboard(current_num=0)
            
        await message.delete()
        await main_query[user.user_id].message.edit_text("Input invent weight", reply_markup = markup) 


    async def navigate_page_num_keyboard(self, query: CallbackQuery, callback_data: NumKeyboardCallback, Manager: Manager):
        await query.answer(cache_time=1)

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

    def show_num_keyboard(self, current_num = 0):
        return self.page_num_keyboard(callback = NumKeyboardCallback, current_num = current_num)