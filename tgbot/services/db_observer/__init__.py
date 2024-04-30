from .bills_collection import track_changes
from .tabacco_collection import track_changes as tabacco_changes
changes_observers = [
    track_changes,
    tabacco_changes,
]

__all__ = [
    "changes_observers",
]