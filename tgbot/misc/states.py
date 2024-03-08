from aiogram.fsm.state import StatesGroup, State

class NavigateStorage(StatesGroup):
    menu = State()
    add = State()
    show = State()
    invent = State()

#adding new tabacco form
class Form(StatesGroup):
    brand_type = State()
    brand_name = State()
    brand_new_name = State()
    tabacco_name = State()
    commit = State()

class InventForm(StatesGroup):
    input_weight = State()
    confirm = State()
