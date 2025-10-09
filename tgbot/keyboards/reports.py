import calendar
from datetime import datetime, timedelta
from typing import List

from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .pager import BasicPageGenerator
from .callbacks import ReportNavigateCallback, CalendarCallback


from ..enums.keyboards.reports_keyboard import ReportsButtonActions
from ..enums.keyboards.calendar import CalendarActions
from ..models import Session, User, UserData
from ..misc.history_manager import Manager
from ..misc.calendar import MONTH_EN_PL


class ReportsKeyboards(BasicPageGenerator):
    _navigate_callback = ReportNavigateCallback
    
    async def reports_menu(self):
        keyboard = InlineKeyboardBuilder()

        row = InlineKeyboardBuilder()

        row.button(text = "Pereodic report", callback_data = ReportNavigateCallback(action = ReportsButtonActions.PEREODIC_REPORT.value))
        row.button(text = "View daily reports", callback_data = ReportNavigateCallback(action = ReportsButtonActions.VIEW_REPORTS.value))
        row.button(text = "Employess reports", callback_data = ReportNavigateCallback(action = ReportsButtonActions.EMPLOYEES_REPORTS.value))
        row.button(text = "Report Options", callback_data = ReportNavigateCallback(action = ReportsButtonActions.REPORT_OPTIONS.value))
        row.adjust(1)
        keyboard.attach(row)

        back_button = InlineKeyboardBuilder().button(
                                                text = "Back to Menu", 
                                                callback_data = ReportNavigateCallback(action = ReportsButtonActions.BACK.value))
        back_button.adjust(1)
        keyboard.attach(back_button)

        return keyboard.as_markup()


    async def view_dayly_reports(self, current_page: int):
        keyboard = InlineKeyboardBuilder()

        start_index, end_index = self.indexes(current_page=current_page)
        buttons = self.data[start_index:end_index]

        for raw in buttons:
            try:
                session_total = await Session.count_total(raw.get("id", 0))
                user = await User.get_user_by_user_id(raw.get("user", "system"))
                keyboard.button(text = f"{raw.get('date')} | {user.username} | {session_total.get('total_cost', 0) if session_total else 0}", callback_data = self._navigate_callback(action = ReportsButtonActions.SHOW_REPORT.value, report_id=raw.get("id", 0)))
            except Exception as e:
                print(e)

        keyboard.adjust(1, repeat = True)
        navigate_buttons = self.slide_page(current_page)

        keyboard.row(*navigate_buttons.buttons, width = 5)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Bills menu <<", callback_data = ReportNavigateCallback(action = ReportsButtonActions.BACK.value))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def show_report(self, report_id: int):
        keyboard = InlineKeyboardBuilder()

        session = await Session.generate_report_data(session_id = report_id)
        keyboard.button(text = f"{session.session_data.opened_by.timestamp.date().strftime('%Y-%m-%d')} | Work time {session.session_data.session_active_time.hours}g {session.session_data.session_active_time.minutes}min", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Opened by: {session.session_data.opened_by.user_data.username}", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Closed by: {session.session_data.closed_by.user_data.username}", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Card: {session.total_selling_by_card} pln", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Cash: {session.total_selling_cash} pln", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Chief: {session.total_selling_chief} pln", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        keyboard.button(text = f"Tabacco: {session.total_tabacco}g", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))

        # keyboard.button(text = f"{session.session_data.opened_by}", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))
        # keyboard.button(text = f"{session.session_data.opened_by}", callback_data = self._navigate_callback(action = ReportsButtonActions.STATIC.value))


        keyboard.button(text = "Generate report", callback_data = self._navigate_callback(action = ReportsButtonActions.GENERATE_REPORT.value, report_id=report_id))
        keyboard.adjust(1)

        back_button = InlineKeyboardBuilder()
        back_button.button(text = "<< Back <<", callback_data = ReportNavigateCallback(action = ReportsButtonActions.BACK.value))

        keyboard.attach(back_button)

        return keyboard.as_markup()
    
    async def navigate_page_slider(self, query: CallbackQuery, callback_data: ReportNavigateCallback, Manager: Manager):
        await query.answer()

        current_page = self.get_current_page(callback_data)
        if not current_page:
            return
        
        await Manager.update({"current_page":current_page})
        
        markup = await self.view_dayly_reports(current_page = current_page)

        await query.message.edit_text(text = "View daily reports: ", reply_markup = markup)

    async def inline_calendar(self, year: int = None, month: int = None, selected_range: tuple = None):
        _current_date = datetime.now()

        if not year: year = _current_date.year
        if not month: month = _current_date.month

        keyboard = InlineKeyboardBuilder()

        # First row - Month and Year
        row = InlineKeyboardBuilder()
        row.button(text = f"{MONTH_EN_PL[calendar.month_name[month]]} | {year}", callback_data = CalendarCallback(action = CalendarActions.STATIC.value))
        row.adjust(1)
        keyboard.attach(row)

        # Second row - Weekdays
        row = InlineKeyboardBuilder()
        for day in ["Pn", "Wt", "Śr", "Czw", "Pt", "Sob", "Nie"]:
            row.button(text = day, callback_data = CalendarCallback(action = CalendarActions.STATIC.value))
        row.adjust(7)
        keyboard.attach(row)

        # Days
        month_calendar = calendar.monthcalendar(year, month)

        def _is_in_range(selected_range, day, year, month):
            _low, _high = selected_range
            
            try:
                if _low and _high:
                    return int(datetime(year, month, day).timestamp()) in range(int(datetime.fromisoformat(_low).timestamp()), int(datetime.fromisoformat(_high).timestamp()))
                return False
            except Exception as e:
                print(e)


        def _is_appertain(selected_date, day, year, month):
            return datetime(year, month, day).isoformat() == selected_date

        for week in month_calendar:
            row = InlineKeyboardBuilder()
            for day in week:
                if day == 0:
                    row.button(text = " ", callback_data = CalendarCallback(action = CalendarActions.STATIC.value))
                else:
                    
                    if selected_range and _is_appertain(selected_range[0], day, year, month):
                        row.button(text = f"[{day}>", callback_data = CalendarCallback(action = CalendarActions.SELECT_DAY.value, year=year, month=month, day=day))
                        continue

                    if selected_range and selected_range[1] and _is_appertain(selected_range[1], day, year, month):
                        row.button(text = f"<{day}]", callback_data = CalendarCallback(action = CalendarActions.SELECT_DAY.value, year=year, month=month, day=day))
                        continue

                    if selected_range and selected_range[1] and _is_in_range(selected_range, day, year, month):
                        row.button(text = f"-{day}-", callback_data = CalendarCallback(action = CalendarActions.SELECT_DAY.value, year=year, month=month, day=day))

                    else:
                        row.button(text = f"{day}", callback_data = CalendarCallback(action = CalendarActions.SELECT_DAY.value, year=year, month=month, day=day))

            row.adjust(7)
            keyboard.attach(row)

        #Navigation
        row = InlineKeyboardBuilder()
        row.button(text = "<", callback_data = CalendarCallback(action = CalendarActions.PREV_MONTH.value, year=year, month=month))
        row.button(text = " ", callback_data = CalendarCallback(action = CalendarActions.STATIC.value)) if not (selected_range and selected_range[1] and selected_range[0]) else row.button(text = f"Commit", callback_data = CalendarCallback(action = CalendarActions.COMMIT.value))
        row.button(text = ">", callback_data = CalendarCallback(action = CalendarActions.NEXT_MONTH.value, year=year, month=month))
        row.adjust(3)
        keyboard.attach(row)

        keyboard.attach(InlineKeyboardBuilder().button(text = "Back", callback_data = ReportNavigateCallback(action = ReportsButtonActions.BACK.value)))

        return keyboard.as_markup()
    
    async def calendar_navigate(self, query: CallbackQuery, callback_data: CalendarCallback, Manager: Manager):
        first_selected = await Manager.get_data(key = "first_selected", state = await Manager._history_state.get_state())
        second_selected = await Manager.get_data(key = "second_selected", state = await Manager._history_state.get_state())

        old_date = datetime(int(callback_data.year), int(callback_data.month), 1)

        if callback_data.action == CalendarActions.NEXT_MONTH.value:
            action_date = old_date + timedelta(days = 31)

        else:
            action_date = old_date - timedelta(days = 1)

        markup = await self.inline_calendar(year = action_date.year, month = action_date.month, selected_range = [first_selected, second_selected])
        await query.message.edit_text("Calendar", reply_markup = markup)

    async def select_day(self, query: CallbackQuery, callback_data: CalendarCallback, Manager: Manager):
        await query.answer()
        selected_date = datetime(int(callback_data.year), int(callback_data.month), int(callback_data.day))

        first_selected = await Manager.get_data(key = "first_selected", state = await Manager._history_state.get_state())
        second_selected = await Manager.get_data(key = "second_selected", state = await Manager._history_state.get_state())
        # Here you can implement logic to handle the selected date, e.g., store it in the Manager or generate a report for that date.

        if not first_selected:
            await Manager.update_data("first_selected", selected_date.isoformat())
            markup = await self.inline_calendar(year = selected_date.year, month = selected_date.month, selected_range = [selected_date.isoformat(), None])
            await query.message.edit_text("Calendar", reply_markup = markup)
            return

        if first_selected and not second_selected:
            await Manager.update_data("second_selected", selected_date.isoformat())
            markup = await self.inline_calendar(year = selected_date.year, month = selected_date.month, selected_range = [first_selected, selected_date.isoformat()])
            await query.message.edit_text("Calendar", reply_markup = markup)

        if first_selected and second_selected:
            first_dt = datetime.fromisoformat(first_selected)
            second_dt = datetime.fromisoformat(second_selected)

            # Determine which selected day is closer to the new date
            if abs((selected_date - first_dt).days) <= abs((selected_date - second_dt).days):
                await Manager.update_data("first_selected", selected_date.isoformat())
                markup = await self.inline_calendar(year=selected_date.year, month=selected_date.month, selected_range=[selected_date.isoformat(), second_selected])
                return await query.message.edit_text("Calendar", reply_markup=markup)
            else:
                await Manager.update_data("second_selected", selected_date.isoformat())
                markup = await self.inline_calendar(year=selected_date.year, month=selected_date.month, selected_range=[first_selected, selected_date.isoformat()])
                return await query.message.edit_text("Calendar", reply_markup=markup)
    
    async def employer_report_menu(self):
        keyboard = InlineKeyboardBuilder()
        users: List[UserData] = await User.get_all_users()

        for user in users:
            keyboard.button(text = f"{user.username} | {user.post.name} | {user.hour_price} zł", callback_data = ReportNavigateCallback(action = ReportsButtonActions.SELECT_EMPLOYEE.value, user_id = user.user_id))


        keyboard.button(text = "Back", callback_data = ReportNavigateCallback(action = ReportsButtonActions.BACK.value))
        keyboard.adjust(1, repeat = True)
        return keyboard.as_markup()
    
    # async def employer_report_calendar(self, query: CallbackQuery, callback_data: ReportNavigateCallback, Manager: Manager):