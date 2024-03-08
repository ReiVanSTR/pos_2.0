import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.storage import storage_menu, storage_brand_types, storage_brand, storage_cancel, storage_commit,\
    StorageNavigate, Insert, ShowPageGenerator, NavigatePageKeyboard, InventPageGenerator,\
    storage_invent_menu, NumKeyboardCallback

from ..models import Tabacco
from ..misc.states import NavigateStorage, Form, InventForm

storage_router = Router()



#command(/storage)
@storage_router.message(F.text.startswith('/') & F.text.contains("storage"))
async def storage_start(message: Message, state: FSMContext, callback_data = None):
    await state.set_state(NavigateStorage.menu)

    markup = storage_menu()
    await message.answer("Storage:", reply_markup = markup)

@storage_router.callback_query(StorageNavigate.filter(F.button_name == "main"))
async def storage_back(query: CallbackQuery, state: FSMContext):
    await state.set_state(NavigateStorage.menu)

    markup = storage_menu()
    await query.message.edit_text("Storage:", reply_markup = markup)
       

@storage_router.callback_query(StorageNavigate.filter(F.button_name == "add"))
async def storage_add_menu(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(NavigateStorage.add)


    markup = storage_brand_types()
    await query.message.edit_text("Select brand type", reply_markup = markup)

    await state.set_state(Form.brand_type)
    
@storage_router.callback_query(Form.brand_type, Insert.filter(F.brand_type))
async def storage_chooise_type(query: CallbackQuery, callback_data: Insert, state: FSMContext):
    await query.answer()

    await state.set_data(data = {"brand_type":callback_data.brand_type})
    await query.message.edit_text("Select brand name", reply_markup = await storage_brand(callback_data.brand_type))

    await state.set_state(Form.brand_name)

@storage_router.callback_query(Form.brand_name, StorageNavigate.filter(F.button_name == "new_brand"))
async def storage_chooise_brand_name(query: CallbackQuery, state: FSMContext):
    await query.answer()

    await query.message.edit_text("Write name for new tabacco brand", reply_markup = storage_cancel())
    await state.set_state(Form.brand_new_name)

@storage_router.message(Form.brand_new_name, F.text.is_not(None))
async def storage_choose_new_brand_name(message: Message, state: FSMContext):
    await state.update_data(data = {"brand_name":message.text}) 
    await message.answer("Write name for " + message.text, reply_markup = storage_cancel())

    await state.set_state(Form.tabacco_name)

@storage_router.callback_query(Form.brand_name, Insert.filter(F.brand_name))
async def storage_chooise_name(query: CallbackQuery, callback_data: Insert, state: FSMContext):
    await query.answer()
    await state.update_data(data = {"brand_name":callback_data.brand_name})    
    await query.message.edit_text("Write name for "+ callback_data.brand_name, reply_markup = storage_cancel())

    await state.set_state(Form.tabacco_name)

@storage_router.message(Form.tabacco_name, F.text.is_not(None))
async def storage_new_name(message: Message, state: FSMContext):
    await state.update_data(data = {"tabacco_name":message.text.strip("")})

    data = await state.get_data()

    msg = \
    f"""
    Brand type: {data["brand_type"]} \n
    Brand name: {data["brand_name"]} \n
    Tabacco name: {data["tabacco_name"]} \n

    All is ok?
    """
    markup = storage_commit()

    await message.answer(text = msg, reply_markup = markup)
    await state.set_state(Form.commit)

@storage_router.callback_query(Form.commit, Insert.filter(F.commit))
async def storage_commit_form(query: CallbackQuery, callback_data: Insert, state: FSMContext):
    await state.set_state(Form.brand_type)
    data = await state.get_data()
    markup = storage_brand_types()
    if callback_data.commit == "yes":
        try:
            await Tabacco.create(label = data["tabacco_name"], brand = data["brand_name"], type = data["brand_type"])
        except Exception as e:
            pass
        await query.message.edit_text("Sucessfully created!")
    else:
        await query.message.edit_text("Operation canceled!")

    await query.message.edit_text("Select brand type", reply_markup = markup)


#show

show_page_generator = ShowPageGenerator()
show_page_generator.connect_router(storage_router)
show_page_generator.register_handler(show_page_generator.navigate_callbacks, [NavigateStorage.show, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next"]))])

@storage_router.callback_query(StorageNavigate.filter(F.button_name == "show"))
async def storage_show(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(NavigateStorage.show)

    show_page_generator.update(await Tabacco.get_all())

    markup = show_page_generator.show_page_keyboard()

    await query.message.edit_text("Storage:", reply_markup = markup)


#inventarization
    
invent_page_generator = InventPageGenerator()
invent_page_generator.connect_router(storage_router)
invent_page_generator.register_handler(invent_page_generator.navigate_page_slider, [NavigateStorage.invent, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next"]))])
invent_page_generator.register_handler(invent_page_generator.navigate_page_num_keyboard, [InventForm.input_weight, NumKeyboardCallback.filter()])

@storage_router.callback_query(StorageNavigate.filter(F.button_name == "invent"))
async def storage_invent_show(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(NavigateStorage.invent)

    markup = storage_invent_menu()
    # await state.set_data({"last_markup":markup})   

    await query.message.edit_text("Inventarization menu:", reply_markup = markup)

@storage_router.callback_query(NavigateStorage.invent, StorageNavigate.filter(F.button_name == "single"))
async def storage_choose_invent_type(query: CallbackQuery, state: FSMContext):
    await query.answer()

    invent_page_generator.update(await Tabacco.get_all())

    markup = invent_page_generator.show_page_keyboard()

    await query.message.edit_text("Single invent:", reply_markup = markup)

@storage_router.callback_query(NavigateStorage.invent, NavigatePageKeyboard.filter(F.action == "select_button"))
async def storage_start_invent(query: CallbackQuery, callback_data: NavigatePageKeyboard, state: FSMContext):
    await query.answer()

    await state.set_state(InventForm.input_weight)
    await state.set_data({"current_num":0})

    markup = invent_page_generator.show_num_keyboard(0)

    document = await Tabacco.get_by_id(callback_data.tabacco_id)
    await query.message.edit_text(document.to_dict().__str__(), reply_markup = markup)
