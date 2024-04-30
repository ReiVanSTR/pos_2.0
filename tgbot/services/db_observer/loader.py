import asyncio
from cachetools import TTLCache
from . import changes_observers

async def start_observers(cache: TTLCache):
    corrotines = [observer(cache) for observer in changes_observers]

    await asyncio.gather(*corrotines)

def observers(cache: TTLCache):
    corrotines = [observer(cache) for observer in changes_observers]
    return corrotines