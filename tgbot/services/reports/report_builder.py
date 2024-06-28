from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from tgbot.models import ObjectId, Session
from .session_dataclasses import SessionReportData

from enum import Enum
from typing import Union
from datetime import datetime
from pytz import timezone

tzinfo = timezone("Europe/Warsaw")

class DocumentBuilder():
    path: str

    def __init__(self, path: str = "./") -> None:
        self.path = path
        self.document = Document()

    def add_title(self, text):
        heading = self.document.add_heading(level=0)
        run = heading.add_run()
        run.text = text
        run.bold = True
        run.font.size = Pt(32)
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def add_heading(self, text, aligment: WD_PARAGRAPH_ALIGNMENT, color: RGBColor = RGBColor(0,0,0)):
        heading = self.document.add_heading(level = 2)
        run = heading.add_run()
        run.text = text
        run.bold = True
        run.font.size = Pt(24)
        run.font.color.rgb = color
        heading.alignment = aligment
        p = self.document.add_paragraph()
        x = p.add_run("text")


    def add_section_heading(self, text, aligment: WD_PARAGRAPH_ALIGNMENT, color: RGBColor = RGBColor(0,0,0)):
        heading = self.document.add_heading(level = 4)
        run = heading.add_run()
        run.text = text
        run.bold = True
        run.font.size = Pt(16)
        run.font.color.rgb = color
        heading.alignment = aligment

    def add_entry(self):
        pass

    def save(self, path: str = "./", document_name: str = "document"):
        if path:
            self.path = path

        self.document.save(f"{path}/{document_name}.docx")

class ReportType(Enum):
    CHANGE = "CHANGE_REPORT"
    PERIODIC = "PERIODIC_REPORT"




class Report():

    def __init__(self) -> None:
        self.builder = DocumentBuilder()

    async def generate_change_report(self, session_id: Union[ObjectId, str], user_name):
        _session_data: SessionReportData = await Session.generate_report_data(session_id = session_id)
        _generating_date = datetime.now(tz=tzinfo).strftime("%d-%m-%Y %H:%M")

        self.builder.add_title(f"Raport zmianowy nr {_session_data.session_data.session_id.__str__()[8:15]}")
        self.builder.add_section_heading(text = f"Data wygenerowania raportu: {_generating_date}. \n Wygenerowany przez: {user_name}", aligment=WD_PARAGRAPH_ALIGNMENT.CENTER)

        self.builder.save(document_name = f"raport_zmianowy_{datetime.now(tz=tzinfo).strftime('%d-%m-%Y')}")


