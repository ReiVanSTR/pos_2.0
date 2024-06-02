import logging
from ..models import Session, SessionData

class SessionManager():

    def __init__(self, session_data: SessionData = None) -> None:
        self.session_data = session_data

    async def open_session(self, opeden_by: int):
        if not self.session_data:
            self.session_data = await Session.open_session(opeden_by)