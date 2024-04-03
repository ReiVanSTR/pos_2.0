"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .echo import echo_router
from .user import menu_router
from .storage import storage_router
from .orders import orders_router

routers_list = [
    storage_router,
    admin_router,
    menu_router,
    orders_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]
