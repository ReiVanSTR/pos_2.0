import logging
from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

from tgbot import keyboards
from ..models import Tabacco, TabaccoData
 
menu = ["Add", "Invent", "Show"]

brand_types = ["Standart", "Premium", "Mix"]

class StorageNavigate(CallbackData, prefix = "storage"):
    button_name: str
    type: str #category, sub-category

#add form Callback class
class Insert(CallbackData, prefix = "insert"):
    brand_type: Optional[str] = None
    brand_name: Optional[str] = None
    tabacco_name: Optional[str] = None
    commit: Optional[str] = None

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int

def storage_menu():
    keyboard = InlineKeyboardBuilder()

    for menu_button in menu:
        keyboard.button(
            text = menu_button,
            callback_data = StorageNavigate(button_name = menu_button.lower(), type = "category")
        )

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
        callback_data = StorageNavigate(button_name = "main", type = "main")
    )

    keyboard.adjust(3, 1)

    return keyboard.as_markup()

async def storage_brand(type: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    brands = await Tabacco.get_all_brands_by_type(type)

    keyboard.button(
        text = "New brand",
        callback_data = StorageNavigate(button_name = "new_brand", type = "None")
    )

    for brand in brands:
        keyboard.button(
            text = brand,
            callback_data = Insert(brand_name = brand)
        )

    keyboard.button(
        text = "<<",
        callback_data = StorageNavigate(button_name = "add", type = "category")
    )

    keyboard.adjust(1,3,3,1)
    return keyboard.as_markup()


def storage_commit():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text = "Yes",
        callback_data = Insert(commit = "yes")
    )

    keyboard.button(
        text = "Nope",
        callback_data = Insert(commit = "no")
    )
    keyboard.adjust(1,1)
    return keyboard.as_markup()

class BasicPageGenerator():
    _router: Router

    @classmethod
    def connect_router(cls, router: Router):
        cls._router = router
    
    @classmethod
    def register_handler(cls, handler, filters):
        cls._router.callback_query.register(handler, *filters)


class ShowPageGenerator(BasicPageGenerator):
    def __init__(self, data: List[TabaccoData] = []) -> None:
        self.data = data
        self.buttons_per_page = 4
        self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil

    def update(self, data):
        self.data = data
        self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil
        
    def show_page_keyboard(self, current_page: int = 1):
        keyboard = InlineKeyboardBuilder()

        start_index = (current_page - 1) * self.buttons_per_page
        end_index = min(start_index + self.buttons_per_page, len(self.data))

        buttons = self.data[start_index:end_index]

        for raw in buttons:
            keyboard.button(
                text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
                callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
            )

        keyboard.adjust(1, repeat = True)

        navigate_buttons = InlineKeyboardBuilder()

        if self.number_of_pages > 1:
            if current_page == 1:
                navigate_buttons.button(
                    text = f" {current_page}/{self.number_of_pages} ",
                    callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
                )
                navigate_buttons.button(
                    text = ">",
                    callback_data = NavigatePageKeyboard(action = "next", current_page = current_page)
                )
                navigate_buttons.button(
                    text = ">>",
                    callback_data = NavigatePageKeyboard(action = "last", current_page = current_page)
                )
                navigate_buttons.adjust(3,1)
            elif current_page == self.number_of_pages and self.number_of_pages > 1:
                navigate_buttons.button(
                    text = "<<",
                    callback_data = NavigatePageKeyboard(action = "first", current_page = current_page)
                )

                navigate_buttons.button(
                    text = "<",
                    callback_data = NavigatePageKeyboard(action = "prev", current_page = current_page)
                )
                navigate_buttons.button(
                    text = f" {current_page}/{self.number_of_pages} ",
                    callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
                )
                navigate_buttons.adjust(3,1)

            else:
                navigate_buttons.button(
                    text = "<<",
                    callback_data = NavigatePageKeyboard(action = "first", current_page = current_page)
                )
                navigate_buttons.button(
                    text = "<",
                    callback_data = NavigatePageKeyboard(action = "prev", current_page = current_page)
                )
                navigate_buttons.button(
                    text = f" {current_page}/{self.number_of_pages} ",
                    callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
                )
                navigate_buttons.button(
                    text = ">",
                    callback_data = NavigatePageKeyboard(action = "next", current_page = current_page)
                )
                navigate_buttons.button(
                    text = ">>",
                    callback_data = NavigatePageKeyboard(action = "last", current_page = current_page)
                )
                navigate_buttons.adjust(5,1)
        else:
            navigate_buttons.button(
                    text = f" {current_page}/{self.number_of_pages} ",
                    callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
                )
            navigate_buttons.adjust(1,1)

        keyboard.attach(navigate_buttons)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Storage <<",callback_data = StorageNavigate(button_name = "main", type = "main"))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def navigate_callbacks(self, query: CallbackQuery, callback_data = NavigatePageKeyboard):
        await query.answer()

        if callback_data.action == "first":
            current_page = 1

        if callback_data.action == "last":
            current_page = self.number_of_pages
        
        if callback_data.action == "prev":
            current_page = callback_data.current_page - 1
        
        if callback_data.action == "next":
            current_page = callback_data.current_page + 1
        
        markup = self.show_page_keyboard(current_page = current_page)

        await query.message.edit_text(text = "Storage", reply_markup = markup)

        

async def storage_show():
    pass