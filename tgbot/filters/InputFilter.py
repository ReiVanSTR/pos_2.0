from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from tgbot.config import Config



class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: TelegramObject) -> bool:
        return (obj.from_user.id in config.tg_bot.admin_ids) == self.is_admin