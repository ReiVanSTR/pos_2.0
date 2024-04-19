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


class OrderStates(StatesGroup):
    open_bill = State()

    


####
class BillStates(StatesGroup):
    bills_menu = State()
    bills_list = State()
    open_bill = State()
    close_bill = State()
    new_bill = State()

    edit_order = State()

class MenuStates(StatesGroup):
    menu = State()

class FormNewBill(StatesGroup):
    input_name = State()
    confirm = State()

class NewOrder(StatesGroup):
    new_order = State()
    new_hookah = State()
    open_cart = State()
    choose_tabacco = State()
    edit_weight = State()
    choose_cost = State()

    open_order = State()