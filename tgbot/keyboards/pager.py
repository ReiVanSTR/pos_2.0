import logging
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict, AnyStr, ClassVar

class NavigatePageKeyboard(CallbackData, prefix = "page_callback"):
    action: str #first, prev, next, last, static
    current_page: int
    kwargs: Optional[str] = ""

class BasicButtons():
    pass

class BasicPageGenerator():
    _router: Router
    _buttons_per_page = 6
    _number_of_pages = 0
    _cache: Dict = {}
    data: List = []
    

    @classmethod
    def connect_router(cls, router: Router):
        cls._router = router
    
    @classmethod
    def indexes(cls, current_page):
        start_index = (current_page - 1) * cls._buttons_per_page
        end_index = min(start_index + cls._buttons_per_page, len(cls.data))

        return start_index, end_index

    @classmethod
    def register_handler(cls, handler, filters):
        cls._router.callback_query.register(handler, *filters)

    @classmethod
    def register_message_handler(cls, handler, filters):
        cls._router.message.register(handler, *filters)

    @classmethod
    def update(cls, data):
        cls.data = data
        cls._number_of_pages = -(-len(cls.data) // cls._buttons_per_page)
    
    @classmethod
    def page_bottom_slider(cls, current_page, callbackdata=NavigatePageKeyboard) -> Dict[str, InlineKeyboardBuilder]:
        static_text = f" {current_page}/{cls._number_of_pages} "
        list_keyboards = {}
        
        empty_page = InlineKeyboardBuilder()  
        empty_page.button(text = static_text, callback_data = callbackdata(action="static", current_page = current_page))
        list_keyboards.update({"empty_page":empty_page})

        first_page = InlineKeyboardBuilder()

        first_page.button(text = static_text, callback_data = callbackdata(action="static", current_page = current_page))
        first_page.button(text = ">", callback_data = callbackdata(action="next", current_page = current_page))
        first_page.button(text = ">>", callback_data = callbackdata(action="last", current_page = current_page))
        first_page.adjust(3,1)
        list_keyboards.update({"first_page":first_page})


        last_page = InlineKeyboardBuilder()

        last_page.button(text = "<<", callback_data = callbackdata(action="first", current_page = current_page))
        last_page.button(text = "<", callback_data = callbackdata(action="prev", current_page = current_page)) 
        last_page.button(text = static_text, callback_data = callbackdata(action="static", current_page = current_page))
        last_page.adjust(3,1)
        list_keyboards.update({"last_page":last_page})

        default_page = InlineKeyboardBuilder()

        default_page.button(text = "<<", callback_data = callbackdata(action="first", current_page = current_page))
        default_page.button(text = "<", callback_data = callbackdata(action="prev", current_page = current_page))
        default_page.button(text = static_text, callback_data = callbackdata(action="static", current_page = current_page))
        default_page.button(text = ">", callback_data = callbackdata(action="next", current_page = current_page))
        default_page.button(text = ">>", callback_data = callbackdata(action="last", current_page = current_page))
        list_keyboards.update({"default_page":default_page})

        return list_keyboards
    
    @classmethod
    def slide_page(cls, current_page):
        # cached_buttons = cls._cache.get("page_bottom_keyboards")
        # navigate_buttons = cached_buttons if cached_buttons else cls.page_bottom_slider(current_page)
        navigate_buttons = cls.page_bottom_slider(current_page)
         
        if cls._number_of_pages > 1:
            if current_page == 1:
                return navigate_buttons["first_page"]
            elif current_page == cls._number_of_pages and cls._number_of_pages > 1:
                return navigate_buttons["last_page"]
            else:
                return navigate_buttons["default_page"]
        else:
            return navigate_buttons["empty_page"]

    @classmethod
    def get_current_page(cls, callback_data):

        actions = {
            "static":None,
            "redraw":callback_data.current_page,
            "first":1,
            "last":cls._number_of_pages,
            "prev":int(callback_data.current_page) - 1,
            "next":int(callback_data.current_page) + 1
        }

        return actions[callback_data.action] if callback_data.action in actions else None

    @classmethod
    def page_num_buttons(cls, callback, current_num):
        keyboard = InlineKeyboardBuilder()

        if not cls._cache.get("num_keyboard_buttons"):
            keyboard.button(text = "-1", callback_data = callback(action = "-1"))
            keyboard.button(text = "-0.5", callback_data = callback(action = "-0.5"))
            keyboard.button(text = "-0.1", callback_data = callback(action = "-0.1"))
            keyboard.button(text = f" {str(current_num)} ", callback_data = callback(action = "static"))
            keyboard.button(text = "+0.1", callback_data = callback(action = "0.1"))
            keyboard.button(text = "+0.5", callback_data = callback(action = "0.5"))
            keyboard.button(text = "1", callback_data = callback(action = "1"))

            keyboard.button(text = "-100", callback_data = callback(action = "-100"))
            keyboard.button(text = "-10", callback_data = callback(action = "-10"))
            keyboard.button(text = "-5", callback_data = callback(action = "-5"))
            keyboard.button(text = " Clear ", callback_data = callback(action = "clear"))
            keyboard.button(text = "+5", callback_data = callback(action = "5"))
            keyboard.button(text = "+10", callback_data = callback(action = "10"))
            keyboard.button(text = "+100", callback_data = callback(action = "100"))
            keyboard.adjust(7,7)
            commit_button = InlineKeyboardBuilder().button(text = "Commit", callback_data = callback(action = "commit").pack())
            keyboard.attach(commit_button)
            cls._cache.update({"num_keyboard_buttons":keyboard.export()})

    @classmethod
    def page_num_keyboard(cls, callback, current_num):
        if not cls._cache.get("num_keyboard_buttons"):
            cls.page_num_buttons(callback, current_num)
        
        cached_buttons = cls._cache.get("num_keyboard_buttons")
        new_current_num_button = InlineKeyboardBuilder().button(text = f" {str(current_num)} ", callback_data = callback(action = "static")).export()[0][0]
        cached_buttons[0][3] = new_current_num_button

        keyboard = InlineKeyboardBuilder(cached_buttons)

        return keyboard.as_markup()
    
    
    # @classmethod
    # def orders_commit(cls, callback):
    #     keyboard = InlineKeyboardBuilder()

    #     keyboard.button(
    #         text = "Yes",
    #         callback_data = callback(commit = "yes")
    #     )

    #     keyboard.button(
    #         text = "Nope",
    #         callback_data = callback(commit = "no")
    #     )
    #     keyboard.adjust(1,1)
    #     return keyboard.as_markup()
    
    @classmethod
    def filters(cls):
        pass