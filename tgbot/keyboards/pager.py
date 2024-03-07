import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Dict, AnyStr

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


# # class ShowPageGenerator(BasicPageGenerator):
#     def __init__(self, data: List[TabaccoData] = []) -> None:
#         self.data = data
#         self.buttons_per_page = 4
#         self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil

#     def update(self, data):
#         self.data = data
#         self.number_of_pages = -(-len(self.data) // self.buttons_per_page) #math.ceil
        
#     def show_page_keyboard(self, current_page: int = 1):
#         keyboard = InlineKeyboardBuilder()

#         start_index = (current_page - 1) * self.buttons_per_page
#         end_index = min(start_index + self.buttons_per_page, len(self.data))

#         buttons = self.data[start_index:end_index]

#         for raw in buttons:
#             keyboard.button(
#                 text = f"{raw.type} | {raw.brand} - {raw.label} - {raw.weight}g",
#                 callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
#             )

#         keyboard.adjust(1, repeat = True)

#         navigate_buttons = InlineKeyboardBuilder()

#         if self.number_of_pages > 1:
#             if current_page == 1:
#                 navigate_buttons.button(
#                     text = f" {current_page}/{self.number_of_pages} ",
#                     callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = ">",
#                     callback_data = NavigatePageKeyboard(action = "next", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = ">>",
#                     callback_data = NavigatePageKeyboard(action = "last", current_page = current_page)
#                 )
#                 navigate_buttons.adjust(3,1)
#             elif current_page == self.number_of_pages and self.number_of_pages > 1:
#                 navigate_buttons.button(
#                     text = "<<",
#                     callback_data = NavigatePageKeyboard(action = "first", current_page = current_page)
#                 )

#                 navigate_buttons.button(
#                     text = "<",
#                     callback_data = NavigatePageKeyboard(action = "prev", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = f" {current_page}/{self.number_of_pages} ",
#                     callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
#                 )
#                 navigate_buttons.adjust(3,1)

#             else:
#                 navigate_buttons.button(
#                     text = "<<",
#                     callback_data = NavigatePageKeyboard(action = "first", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = "<",
#                     callback_data = NavigatePageKeyboard(action = "prev", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = f" {current_page}/{self.number_of_pages} ",
#                     callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = ">",
#                     callback_data = NavigatePageKeyboard(action = "next", current_page = current_page)
#                 )
#                 navigate_buttons.button(
#                     text = ">>",
#                     callback_data = NavigatePageKeyboard(action = "last", current_page = current_page)
#                 )
#                 navigate_buttons.adjust(5,1)
#         else:
#             navigate_buttons.button(
#                     text = f" {current_page}/{self.number_of_pages} ",
#                     callback_data = NavigatePageKeyboard(action = "static", current_page = current_page)
#                 )
#             navigate_buttons.adjust(1,1)

#         keyboard.attach(navigate_buttons)

#         back_button = InlineKeyboardBuilder()
#         back_button.button(text = "<< Storage <<",callback_data = StorageNavigate(button_name = "main", type = "main"))

#         keyboard.attach(back_button)

#         return keyboard.as_markup()
    
#     async def navigate_callbacks(self, query: CallbackQuery, callback_data = NavigatePageKeyboard):
#         await query.answer()

#         if callback_data.action == "first":
#             current_page = 1

#         if callback_data.action == "last":
#             current_page = self.number_of_pages
        
#         if callback_data.action == "prev":
#             current_page = callback_data.current_page - 1
        
#         if callback_data.action == "next":
#             current_page = callback_data.current_page + 1
        
#         markup = self.show_page_keyboard(current_page = current_page)

#         await query.message.edit_text(text = "Storage", reply_markup = markup)