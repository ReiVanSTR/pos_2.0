import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict, AnyStr, ClassVar

class BasicButtons():
    pass

class BasicPageGenerator():
    _router: Router

    @classmethod
    def connect_router(cls, router: Router):
        cls._router = router
    
    @classmethod
    def register_handler(cls, handler, filters):
        cls._router.callback_query.register(handler, *filters)
    
    @classmethod
    def page_bottom_slider(cls,
            first: CallbackData, 
            prev: CallbackData,
            next: CallbackData,
            last: CallbackData,
            static_callback: CallbackData,
            static_text: AnyStr
            ) -> Dict[str, InlineKeyboardBuilder]:
        
        list_keyboards = {}
        
        empty_page = InlineKeyboardBuilder()  
        empty_page.button(text = static_text, callback_data="static")
        list_keyboards.update({"empty_page":empty_page})

        first_page = InlineKeyboardBuilder()

        first_page.button(text = static_text, callback_data = static_callback)
        first_page.button(text = ">", callback_data = next)
        first_page.button(text = ">>", callback_data = last)
        first_page.adjust(3,1)
        list_keyboards.update({"first_page":first_page})


        last_page = InlineKeyboardBuilder()

        last_page.button(text = "<<", callback_data = first)
        last_page.button(text = "<", callback_data = prev) 
        last_page.button(text = static_text, callback_data = static_callback)
        last_page.adjust(3,1)
        list_keyboards.update({"last_page":last_page})

        default_page = InlineKeyboardBuilder()

        default_page.button(text = "<<", callback_data = first)
        default_page.button(text = "<", callback_data = prev)
        default_page.button(text = static_text, callback_data = static_callback)
        default_page.button(text = ">", callback_data = next)
        default_page.button(text = ">>", callback_data = last)
        list_keyboards.update({"default_page":default_page})

        return list_keyboards

    @classmethod
    def page_num_keyboard(cls, callback, current_num):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text = "-1", callback_data = callback(action = "-1"))
        keyboard.button(text = "-0.5", callback_data = callback(action = "-0.5"))
        keyboard.button(text = "-0.1", callback_data = callback(action = "-0.1"))
        keyboard.button(text = str(current_num), callback_data = callback(action = "static"))
        keyboard.button(text = "+0.1", callback_data = callback(action = "0.1"))
        keyboard.button(text = "+0.5", callback_data = callback(action = "0.5"))
        keyboard.button(text = "1", callback_data = callback(action = "1"))

        keyboard.button(text = "-100", callback_data = callback(action = "-100"))
        keyboard.button(text = "-10", callback_data = callback(action = "-10"))
        keyboard.button(text = "-5", callback_data = callback(action = "-5"))
        keyboard.button(text = "clear", callback_data = callback(action = "clear"))
        keyboard.button(text = "+5", callback_data = callback(action = "5"))
        keyboard.button(text = "+10", callback_data = callback(action = "10"))
        keyboard.button(text = "+100", callback_data = callback(action = "100"))

        keyboard.adjust(7,7)

        return keyboard.as_markup()
    
    @classmethod
    def filters(cls):
        pass