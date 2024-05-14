import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from tgbot.keyboards.storage import storage_menu, storage_brand_types, storage_brand, storage_cancel, storage_commit,\
    StorageNavigate, Insert, StorageCommit, ShowPageGenerator, NavigatePageKeyboard, InventPageGenerator,\
    storage_invent_menu, NumKeyboardCallback

from ..models import Tabacco, Invent, Changes, UserData
from ..misc.states import StorageStates, Form, InventForm, MenuStates
from ..keyboards.callbacks import MenuNavigateCallback
from ..keyboards.menu import MenuKeyboards
from ..misc.history_manager import Manager
from ..misc.main_query import main_query

from datetime import datetime

storage_router = Router()


#command(/storage)
@storage_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "storage"))
async def storage_start(query: CallbackQuery, Manager: Manager):
    await query.answer(text = "Opening storage")
    await Manager.push(StorageStates.menu)

    markup = storage_menu()
    await query.message.edit_text("Storage:", reply_markup = markup) #noqa


#Addind brand/tabacco operation
@storage_router.callback_query(StateFilter(StorageStates.menu), StorageNavigate.filter(F.action == "add"))
async def storage_add(query: CallbackQuery, Manager: Manager):
    await query.answer(text = "Loading ...")
    await Manager.push(StorageStates.add)


    markup = storage_brand_types()
    await query.message.edit_text("Select brand type", reply_markup = markup)


@storage_router.callback_query(StateFilter(StorageStates.add), Insert.filter(F.brand_type))
async def storage_chooise_type(query: CallbackQuery, callback_data: Insert, Manager: Manager):
    await query.answer(text = "Loading ...")

    await Manager.push(state = Form.brand_type, data = {"brand_type":callback_data.brand_type})
    await query.message.edit_text("Select brand name", reply_markup = await storage_brand(callback_data.brand_type))


@storage_router.callback_query(StateFilter(Form.brand_type), StorageNavigate.filter(F.action == "new_brand"))
async def storage_chooise_brand_name(query: CallbackQuery, Manager: Manager, user: UserData):
    await query.answer(text = "Loading ...")
    await Manager.push(state = Form.brand_new_name, push = True)

    await query.message.edit_text("Write name for new tabacco brand", reply_markup = storage_cancel())
    main_query[user.user_id] = query


@storage_router.message(StateFilter(Form.brand_new_name), F.text.is_not(None))
async def storage_choose_new_brand_name(message: Message, Manager: Manager, user: UserData):
    await Manager.push(state = Form.tabacco_name, data = {"brand_name":message.text}, push = True)

    await message.delete()
    await main_query[user.user_id].message.edit_text(f"Write name for {message.text} brand", reply_markup = storage_cancel())



@storage_router.callback_query(StateFilter(Form.brand_type), Insert.filter(F.brand_name))
async def storage_chooise_name(query: CallbackQuery, callback_data: Insert, Manager: Manager, user: UserData):
    await query.answer(text = "Loading...")
    await Manager.push(state = Form.tabacco_name, data = {"brand_name":callback_data.brand_name}, push = True)

    await query.message.edit_text("Write name for "+ callback_data.brand_name, reply_markup = storage_cancel())
    main_query[user.user_id] = query


@storage_router.message(Form.tabacco_name, F.text.is_not(None))
async def storage_new_name(message: Message, Manager: Manager, user: UserData):
    await Manager.push(state = Form.commit, data = {"tabacco_name":message.text.strip("")}, push = True)

    data = await Manager.get_all_data()

    msg = \
    f"""
    Brand type: {data["brand_type"]} \n
    Brand name: {data["brand_name"]} \n
    Tabacco name: {data["tabacco_name"]} \n

    All is ok?
    """
    markup = storage_commit(StorageCommit)

    await message.delete()
    await main_query[user.user_id].message.edit_text(text = msg, reply_markup = markup)


@storage_router.callback_query(StateFilter(Form.commit), StorageCommit.filter(F.commit))
async def storage_commit_form(query: CallbackQuery, callback_data: StorageCommit, Manager: Manager):
    await query.answer(text = "Loading ...")
    data = await Manager.get_all_data()
    await Manager.goto(go_to = Form.brand_type)
    
    _state_record = await Manager.get()
    if callback_data.commit == "yes":
        try:
            await Tabacco.create_tabacco(label = data["tabacco_name"], brand = data["brand_name"], type = data["brand_type"])
        except Exception as error:
            raise error
        await query.message.edit_text("Sucessfully created!")
    else:
        await query.message.edit_text("Operation canceled!")

    markup = await storage_brand(_state_record.data.get("brand_type"))
    await query.message.edit_text("Select brand type", reply_markup = markup)

@storage_router.callback_query(StorageNavigate.filter(F.action == "back"))
async def storage_back(query: CallbackQuery, Manager: Manager, state: FSMContext, user):
    await query.answer()
    await Manager.pop()
    _state_record = await Manager.get()

    await state.set_state(_state_record.state)

    brand_type = _state_record.data.get("brand_type", None)
    if _state_record.state == "StorageStates:show":
        show_page_generator.update(await Tabacco.get_all())


    markups = {
        "MenuStates:menu":await MenuKeyboards().menu_keyboard(user = user),
        "StorageStates:menu":storage_menu(),
        "StorageStates:add":storage_brand_types(),
        "StorageStates:show":show_page_generator.show_page_keyboard(),
        "Form:brand_type":await storage_brand(brand_type) if brand_type else None,
    }

    reply_text = {
        "MenuStates:menu":"Menu",
        "StorageStates:menu":"Storage",
        "StorageStates:add":"Select brand name",
        "StorageStates:show":"Storage",
        "Form:brand_type":"Select brand type",
    }

    text = reply_text.get(_state_record.state)
    markup = markups.get(_state_record.state)
    await query.message.edit_text(text = text, reply_markup = markup) 




#show

show_page_generator = ShowPageGenerator()
show_page_generator.connect_router(storage_router)
show_page_generator.register_handler(show_page_generator.navigate_callbacks, [StorageStates.show, NavigatePageKeyboard.filter(F.action.in_(["static", "redraw", "prev","next","last","first"]))])

@storage_router.callback_query(StateFilter(StorageStates.menu), StorageNavigate.filter(F.action == "show"))
async def storage_show(query: CallbackQuery, Manager: Manager):
    await query.answer()
    await Manager.push(StorageStates.show)

    show_page_generator.update(await Tabacco.get_all())

    markup = show_page_generator.show_page_keyboard()

    await query.message.edit_text("Storage:", reply_markup = markup)

@storage_router.callback_query(StateFilter(StorageStates.show), NavigatePageKeyboard.filter(F.action == "show_tabacco"))
async def storage_show_history(query: CallbackQuery, callback_data: NavigatePageKeyboard, Manager: Manager):
    await query.answer()
    await Manager.push(StorageStates.show_tabacco, {"tabacco_id":callback_data.tabacco_id})
    markup = await show_page_generator.tabacco_history_keyboard(tabacco_id = callback_data.tabacco_id, current_page = callback_data.current_page)

    await query.message.edit_text(text = "Inventarization scope", reply_markup = markup)

@storage_router.callback_query(StateFilter(StorageStates.show_tabacco), StorageNavigate.filter(F.action == "show_checkbox"))
async def storage_show_checkbox(query: CallbackQuery, Manager: Manager):
    await query.answer()
    _state_record = await Manager.get()
    tabacco_id = _state_record.data.get("tabacco_id")

    await Tabacco.change_visibility(tabacco_id)
    markup = await show_page_generator.tabacco_history_keyboard(tabacco_id = tabacco_id, current_page = 1)

    await query.message.edit_text(text = "Inventarization scope", reply_markup = markup)



#inventarization
    
invent_page_generator = InventPageGenerator()
invent_page_generator.connect_router(storage_router)
invent_page_generator.register_handler(invent_page_generator.navigate_page_slider, [InventForm.select_tabacco, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next"]))])
invent_page_generator.register_handler(invent_page_generator.navigate_page_num_keyboard, [InventForm.input_weight, NumKeyboardCallback.filter(F.action.not_in(["commit"]))])
invent_page_generator.register_message_handler(invent_page_generator.massage_input, [InventForm.input_weight, F.text.is_not(None)])
@storage_router.callback_query(StateFilter(StorageStates.menu), StorageNavigate.filter(F.action == "invent"))
async def storage_invent_show(query: CallbackQuery, Manager: Manager):
    await query.answer()
    await Manager.push(StorageStates.invent)

    markup = storage_invent_menu()
    # await state.set_data({"last_markup":markup})   

    await query.message.edit_text("Inventarization menu:", reply_markup = markup)

@storage_router.callback_query(StateFilter(StorageStates.invent), StorageNavigate.filter(F.action == "single"))
async def storage_choose_invent_type(query: CallbackQuery, Manager: Manager):
    await query.answer()
    await Manager.push(InventForm.select_tabacco)

    invent_page_generator.update(await Tabacco.get_all())

    markup = invent_page_generator.invent_page_keyboard()

    await query.message.edit_text("Single invent:", reply_markup = markup)

@storage_router.callback_query(StateFilter(InventForm.select_tabacco), NavigatePageKeyboard.filter(F.action == "select_button"))
async def storage_start_invent(query: CallbackQuery, callback_data: NavigatePageKeyboard, Manager: Manager, user):
    await query.answer()
    document = await Tabacco.get_by_id(callback_data.tabacco_id)
    await Manager.push(InventForm.input_weight, {"tabacco_id":callback_data.tabacco_id, "current_num": 0})
    main_query[user.user_id] = query
    markup = invent_page_generator.show_num_keyboard()

    await query.message.edit_text(f"{document.brand} - {document.label} - Expected weight: {document.weight}", reply_markup = markup)

@storage_router.callback_query(InventForm.input_weight, NumKeyboardCallback.filter(F.action == "commit"))
async def storage_confirm_invent(query: CallbackQuery, Manager: Manager):
    await query.answer()
    _state_record = await Manager.get()
    await Manager.push(state = InventForm.confirm, push = True)
    item = await Tabacco.get_by_id(_state_record.data.get("tabacco_id"))

    text = f"{item.brand} - {item.label} \n Expected weight: {item.weight} \n Accepted weight: {_state_record.data.get('current_num')}"

    markup = storage_commit(StorageCommit)
    
    await query.message.edit_text(text, reply_markup = markup)


@storage_router.callback_query(StateFilter(InventForm.confirm), StorageCommit.filter())
async def storage_commit_invent(query: CallbackQuery, callback_data: StorageNavigate, Manager: Manager):
    await query.answer()
    _state_record = await Manager.get()
    await Manager.goto(go_to = InventForm.select_tabacco)
    
    item = await Tabacco.get_by_id(_state_record.data.get("tabacco_id"))

    changes = Changes(_id = 0, timestamp = datetime.now(), user_id = query.from_user.id, expected_weight = item.weight, accepted_weight = _state_record.data.get('current_num'))
    

    if callback_data.commit == "yes":
        try:
            await Invent.update_changes(item._id, changes)
            await Tabacco.update_weight(item._id, changes.accepted_weight)

        except:
            await query.message.edit_text("Operation canceled!")

    invent_page_generator.update(await Tabacco.get_all())
    markup = invent_page_generator.invent_page_keyboard()

    await query.message.edit_text("Single invent:", reply_markup = markup)      
