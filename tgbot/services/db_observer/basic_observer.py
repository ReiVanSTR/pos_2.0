from typing import Dict, Any, List, Optional

from datetime import datetime
from dataclasses import dataclass

from tgbot.models.basic import ObjectId


@dataclass
class UpdateDescription():
    updatedFields: Dict[str, Any]
    removedFields: List
    truncatedArrays: List

@dataclass
class Change():
    _id: str
    documentKey: Dict[str, ObjectId]
    fullDocument: Optional[Dict[str, Any]]
    ns: Dict[str, Any]
    operationType: str
    updateDiscription: Optional[UpdateDescription]
    wallTime: datetime
    clusterTime: dict[str, Any]

    def __init__(self, _id, documentKey, ns, operationType, wallTime, clusterTime, updateDescription = None, fullDocument = None) -> None:
        self._id = _id
        self.documentKey = documentKey
        self.fullDocument = fullDocument
        self.ns = ns
        self.operationType = operationType
        self.updateDiscription = UpdateDescription(**updateDescription) if updateDescription else None
        self.wallTime = wallTime
        self.clusterTime = clusterTime

