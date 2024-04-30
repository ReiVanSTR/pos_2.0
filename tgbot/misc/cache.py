from tgbot.models import Bills, Tabacco
import logging
from functools import wraps
import asyncio
from cachetools import LRUCache


def keygenerator(prefix, key, *args, **kwargs):
    if not kwargs and not args:
        return f"{prefix}_{key}"
    
    key = ""
    if kwargs:
        kwargs_keys = "_"
        for _, value in kwargs.items():
            if not isinstance(value, dict):
                kwargs_keys = kwargs_keys.join(str(value))
        key += kwargs_keys

    if args:
        key += "_".join(map(str, args))
        
    return

def cached(prefix, key, keygen: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Проверяем наличие аргумента 'update' в kwargs
            update_cache = kwargs.get('update', False)

            cache_key = f"{prefix}_{key}"

            if keygen:
                args_key = "_".join(map(str, args[1:]))
                cache_key += args_key
            
            cache = args[0].cache  # Предполагается, что cache хранится в первом аргументе
            logging.log(30, f"current cache: {cache}")
            if not update_cache and cache_key in cache:
                logging.info(f"From cache: {cache_key}")
                return cache[cache_key]

            result = await func(*args, **kwargs)
            cache[cache_key] = result
            return result
        return wrapper
    return decorator

class Cache():
    def __init__(self) -> None:
        self.cache = LRUCache(maxsize=100)
        self.lock = asyncio.Lock()


    # @cachedmethod(cache=lambda self: self.cache, key=partial(keygen, "bills", "all_bills"))
    @cached("bills", "all_bills")
    async def getAllBills(self, filter: dict = {}, *args, **kwargs):
        
        async with self.lock:
            try:
                return await Bills.get_all_bills(filter)
            except:
                logging.error(f"Error with getting All bills")
    
    @cached("orders", "all_tabacco")
    async def getAllTabacco(self):
        return await Tabacco.get_all()
    
    @cached("bills", "bill", keygen = True)
    async def getBill(self, bill_id):
        return await Bills.get_bill(bill_id)
    
    async def update(self, key, data):
        try:
            self.cache[key] = data
            return True
        except:
            logging.log(30, "Error with update data: {data} with key: {key}")


_cache = Cache()