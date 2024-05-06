import logging
import asyncio
from tgbot.models import Bills
from tgbot.misc.cache import Cache

from .basic_observer import Change

async def track_changes(cache: Cache):
    collection = Bills._collection
    lock = asyncio.Lock()

    async with collection.watch(full_document = "updateLookup") as stream: #type: ignore
        async for change in stream:
            change = Change(**change)
            
            async with lock:
                if change.operationType in ["insert", "delete"]:
                    key = "bills_all_bills"
                    data = await Bills.get_all_bills(filtr = {"is_opened":True})
                    await cache.update(key, data)
                    logging.log(30, f"Updated cache with key {key}")

                if change.operationType in ["update"]:
                    document_id = change.documentKey.get("_id").__str__()
                    data = await Bills.get_bill(document_id)
                    key = f"bills_bill_{document_id}"
                    await cache.update(key = key, data = data)

                    logging.log(30, f"Updated cache with key {key}")