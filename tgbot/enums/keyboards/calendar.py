from enum import Enum


class CalendarActions(str, Enum):
    STATIC = "static"
    SELECT_DAY = "select_day"
    PREV_MONTH = "prev_month"
    NEXT_MONTH = "next_month"
    COMMIT = "commit"


    def __repr__(self):
        return self.value