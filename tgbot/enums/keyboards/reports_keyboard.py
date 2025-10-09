from enum import Enum


class ReportsButtonActions(str, Enum):
    BACK = "back"
    PEREODIC_REPORT = "pereodic_report"
    GENERATE_REPORT = "generate_report"
    VIEW_REPORTS = "view_reports"
    DELETE_REPORT = "delete_report"
    REPORT_OPTIONS = "report_options"
    SHOW_REPORT = "show_report"
    STATIC = "static"
    EMPLOYEES_REPORTS = "employees_reports"
    SELECT_EMPLOYEE = "select_employee"
    


    def __repr__(self):
        return self.value
    
