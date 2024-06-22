from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class DocumentBuilder():
    path: str

    def __init__(self, path) -> None:
        self.path = path
        self.document = Document()

    def add_title(self, text, font_size):
        heading = self.document.add_heading(level=0)
        run = heading.add_run()
        run.text = text
        run.font.size = Pt(font_size)
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def add_heading(self, text, level: int, aligment: WD_PARAGRAPH_ALIGNMENT, color: RGBColor = RGBColor(0,0,0)):
        heading = self.document.add_heading(level = level)
        run = heading.add_run()
        run.text = text
        run.bold = True
        # run.font.size = Pt(32)
        run.font.color.rgb = color
        heading.alignment = aligment

    # def add_section_heading(self):
    #     heading = self.document.add_heading(level = level)
    #     run = heading.add_run()
    #     run.text = text
    #     run.bold = True
    #     run.font.size = Pt(32)
    #     run.font.color.rgb = color
    #     heading.alignment = aligment

    def add_entry(self):
        pass

    def save(self, save_path: str = None):
        if save_path:
            self.path = save_path

        self.document.save("path")


class Report():

    def __init__(self) -> None:
        pass