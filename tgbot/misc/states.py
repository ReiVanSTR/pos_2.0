from aiogram.fsm.state import StatesGroup, State

class StorageStates(StatesGroup):
    menu = State()
    add = State()
    show = State()
    show_tabacco = State()
    invent = State()

#adding new tabacco form
class Form(StatesGroup):
    brand_type = State()
    brand_name = State()
    brand_new_name = State()
    tabacco_name = State()
    commit = State()

class InventForm(StatesGroup):
    select_tabacco = State()
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
    options = State()

    edit_order = State()
    discount_order = State()

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

class SessionStates(StatesGroup):
    menu = State()
    activities = State()
    bill_options = State()
    open_order = State()
    change_payment_method = State()
    close_session_commit = State()