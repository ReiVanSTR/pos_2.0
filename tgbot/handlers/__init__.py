"""Import all routers and add them to routers_list."""
from .user import menu_router
from .storage import storage_router
from .orders import orders_router
from .bills import bills_router

routers_list = [
    storage_router,
    menu_router,
    bills_router,
    orders_router,
]

__all__ = [
    "routers_list",
]
