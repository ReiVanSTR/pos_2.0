import random
import logging
from datetime import datetime
from typing import Union
from aiogram.fsm.context import FSMContext

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile

from .markup import onState, Markups, StateKeyboard

from ..models import UserData, Session, User, UserData
from ..keyboards.menu import MenuKeyboards
from ..keyboards.reports import ReportsKeyboards
from ..keyboards.callbacks import MenuNavigateCallback, ReportNavigateCallback, CalendarCallback
from ..keyboards.pager import NavigatePageKeyboard
from ..misc.history_manager import Manager
from ..misc.cache import Cache
from ..misc.states import ReportsStates, MenuStates
from ..enums.keyboards.reports_keyboard import ReportsButtonActions
from ..enums.keyboards.calendar import CalendarActions

from ..models.agregations.sessions_by_date import get_pipeline
from ..services.reports.builder import builder





reports_router = Router()
keyboards = ReportsKeyboards()
keyboards.connect_router(reports_router)

# Register handlers for pagination and pereodic report calendar navigation
keyboards.register_handler(keyboards.navigate_page_slider, [ReportsStates.view_reports, NavigatePageKeyboard.filter(F.action.in_(["first", "last", "prev","next","redraw"]))])
keyboards.register_handler(keyboards.calendar_navigate, [ReportsStates.pereodic_report, CalendarCallback.filter(F.action.in_(["prev_month", "next_month"]))])
keyboards.register_handler(keyboards.select_day, [ReportsStates.pereodic_report, CalendarCallback.filter(F.action == "select_day")])

keyboards.register_handler(keyboards.calendar_navigate, [ReportsStates.employer_report_calendar, CalendarCallback.filter(F.action.in_(["prev_month", "next_month"]))])
keyboards.register_handler(keyboards.select_day, [ReportsStates.employer_report_calendar, CalendarCallback.filter(F.action == "select_day")])

# Show reports menu
@reports_router.callback_query(StateFilter(MenuStates.menu), MenuNavigateCallback.filter(F.button_name == "reports"))
async def show_reports_menu(query: CallbackQuery, user: UserData, cache: Cache, Manager: Manager, logger):
    await query.answer()
    await Manager.push(ReportsStates.reports_menu.state, {})

    await query.message.edit_text("Reports menu:", reply_markup= await keyboards.reports_menu())


# View daily reports
@reports_router.callback_query(StateFilter(ReportsStates.reports_menu), ReportNavigateCallback.filter(F.action == ReportsButtonActions.VIEW_REPORTS.value))
async def view_reports_menu(query: CallbackQuery, Manager: Manager, user: UserData):
    await query.answer()
    await Manager.push(ReportsStates.view_reports.state, {"current_page":1})

    sessions_by_date = Session._collection.aggregate(get_pipeline(datetime.fromisoformat("2025-01-01"), datetime.now()))
    keyboards.update(data = [session async for session in sessions_by_date])

    await query.message.edit_text("View daily reports:", reply_markup= await keyboards.view_dayly_reports(current_page = 1))

@reports_router.callback_query(StateFilter(ReportsStates.view_reports), ReportNavigateCallback.filter(F.action == ReportsButtonActions.SHOW_REPORT.value))
async def show_report(query: CallbackQuery, callback_data: ReportNavigateCallback, Manager: Manager):
    await query.answer()
    await Manager.push(ReportsStates.show_report.state, {"report_id":callback_data.report_id})


    await query.message.edit_text(f"Report details for report id: {callback_data.report_id}", reply_markup= await keyboards.show_report(callback_data.report_id))

@reports_router.callback_query(StateFilter(ReportsStates.show_report), ReportNavigateCallback.filter(F.action == ReportsButtonActions.GENERATE_REPORT.value))
async def generate_report(query: CallbackQuery, callback_data: ReportNavigateCallback, Manager: Manager):
    await query.answer()
    session_id = await Manager.get_data(key = "report_id")

    try:
        await builder.generate_change_report(session_id, "System", "_buffer")

        image = FSInputFile(
            "reports/_buffer.docx",
            filename=f"report_{session_id[6:9]}.docx"
        )
        await query.message.answer_document(document = image)
    except Exception as e:
        print(e)
        await query.message.answer("Error generate report")

# Generate pereodic report
@reports_router.callback_query(StateFilter(ReportsStates.reports_menu), ReportNavigateCallback.filter(F.action == ReportsButtonActions.PEREODIC_REPORT.value))
async def pereodic_report_calendar(query: CallbackQuery, Manager: Manager):
    await query.answer()
    await Manager.push(ReportsStates.pereodic_report.state, {})

    markup = await keyboards.inline_calendar()
    await query.message.edit_text(text = "Select range for pereodic report: ", reply_markup = markup)

@reports_router.callback_query(StateFilter(ReportsStates.pereodic_report), CalendarCallback.filter(F.action == CalendarActions.COMMIT.value))
async def generate_pereodic_report(query: CallbackQuery,Manager: Manager):
    await query.answer()
    first_selected = await Manager.get_data(key = "first_selected")
    second_selected = await Manager.get_data(key = "second_selected")

    try:
        await builder.generate_pereodic_report(datetime.fromisoformat(first_selected), datetime.fromisoformat(second_selected), "System", "_buffer")
        image = FSInputFile(
            "reports/_buffer.docx",
            filename=f"pereodic_report_{first_selected}_{second_selected}.docx"
        )

        await query.message.answer_document(document = image)
        markup = await keyboards.inline_calendar()
        await query.message.edit_text(text = "Select range for pereodic report: ", reply_markup = markup)

    except Exception as e:
        print(e)
        await query.message.answer("Error generate report")

#Employer reports
@reports_router.callback_query(StateFilter(ReportsStates.reports_menu), ReportNavigateCallback.filter(F.action == ReportsButtonActions.EMPLOYEES_REPORTS.value))
async def employer_reports_menu(query: CallbackQuery, Manager: Manager):
    await query.answer()
    await Manager.push(ReportsStates.employer_report_menu.state, {})

    await query.message.edit_text("Select user to generate report:", reply_markup= await keyboards.employer_report_menu())

@reports_router.callback_query(StateFilter(ReportsStates.employer_report_menu), ReportNavigateCallback.filter(F.action == ReportsButtonActions.SELECT_EMPLOYEE.value))
async def select_employee_for_report(query: CallbackQuery, callback_data: ReportNavigateCallback, Manager: Manager):
    await query.answer()
    await Manager.push(ReportsStates.employer_report_calendar.state, {"user_id":callback_data.user_id})

    markup = await keyboards.inline_calendar()
    await query.message.edit_text(text = "Select range for employer report: ", reply_markup = markup)

@reports_router.callback_query(StateFilter(ReportsStates.employer_report_calendar), CalendarCallback.filter(F.action == CalendarActions.COMMIT.value))
async def generate_employer_report(query: CallbackQuery, Manager: Manager):
    await query.answer()
    first_selected = await Manager.get_data(key = "first_selected")
    second_selected = await Manager.get_data(key = "second_selected")
    user_id = await Manager.get_data(key = "user_id")
    _user: UserData = await User.get_user_by_user_id(user_id)

    try:
        await builder.generate_employer_report(
            user_id = user_id,
            from_date = datetime.fromisoformat(first_selected),
            to_date = datetime.fromisoformat(second_selected),
            user_name = "System",
            filename = "_buffer",
            shift_cost = _user.shift_cost,
            hour_price = _user.hour_price,
            count_by_hours = True,
            selling_reward = _user.selling_reward
        )
        image = FSInputFile(
            f"reports/_buffer.docx",
            filename=f"employer_{_user.username}_report_{first_selected}_{second_selected}.docx"
        )

        await query.message.answer_document(document = image)
        await Manager.goto(ReportsStates.employer_report_menu)

        markup = await keyboards.employer_report_menu()
        await query.message.edit_text(text = "Select user to generate report: ", reply_markup = markup)

    except Exception as e:
        print(e)
        await query.message.answer("Error generate report")

#Back
@reports_router.callback_query(ReportNavigateCallback.filter(F.action == ReportsButtonActions.BACK.value))
async def session_back(query: CallbackQuery, Manager: Manager, user: UserData, state: FSMContext):
    await query.answer()
    await Manager.pop()
    _state_record = await Manager.get()
    await state.set_state(_state_record.state)

    markups = Markups()
    
    async def _menu_getter():
        return user
    
    async def _reports_getter():
        return await Manager.get_data(key = "current_page")

    markups.register("Menu",
        StateKeyboard(
            filtr = onState("MenuStates:menu"), 
            text = "Menu", 
            keyboard = MenuKeyboards().menu_keyboard, 
            getter = _menu_getter
        )
    )

    markups.register("ReportsMenu",
        StateKeyboard(
            filtr = onState("ReportsStates:reports_menu"), 
            text = "Reports menu", 
            keyboard = keyboards.reports_menu, 
        )
    )

    markups.register("VievReports",
        StateKeyboard(
            filtr = onState("ReportsStates:view_reports"), 
            text = "View reports", 
            keyboard = keyboards.view_dayly_reports,
            getter = _reports_getter
        )
    )
    markups.register("EmployeesReports",
        StateKeyboard(
            filtr = onState("ReportsStates:employer_report_menu"), 
            text = "Select user to generate report:", 
            keyboard = keyboards.employer_report_menu,
        )
    )

    result = await markups.get_markup(_state_record.state)
    await query.message.edit_text(text = result["text"], reply_markup = result["keyboard"])