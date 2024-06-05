from enum import Enum


class ButtonActions(str, Enum):
    BACK = "back"
    STATIC = "static"

    ACTIVITIES = "activities"
    OPEN_SESSION = "open_session"
    CLOSE_SESSION = "close_session"
    OPEN_BILL = "open_bill"
    CHANGE_PAYMENT_METHOD = "change_payment_method"
    BILL_OPTIONS = "bill_options"
    OPEN_ORDER = "open_order"
    CLOSE_SESSION_COMMIT = "close_session_commit"

    def __repr__(self):
        return self.value