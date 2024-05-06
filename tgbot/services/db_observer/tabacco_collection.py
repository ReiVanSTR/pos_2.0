import logging

from tgbot.models import Tabacco
from tgbot.misc.cache import Cache

from .basic_observer import Change

async def track_changes(cache: Cache):
    collection = Tabacco._collection

    async with collection.watch(full_document = "updateLookup") as stream: #type: ignore
        async for change in stream:
            change = Change(**change)
            
            if change.operationType in ["insert", "delete"]:
                logging.info("Updated cache")
                await cache.getAllBills(filter = {"is_closed": False})

            if change.operationType in ["update"]:
                logging.info("Updated cache")
                await cache.getAllBills(filter = {"is_closed": False})