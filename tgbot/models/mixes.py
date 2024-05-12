from pydantic import Field
from dataclasses import dataclass
from .basic import Basic, ObjectId
from typing import List

@dataclass
class TabaccoComponent(): 
    tabacco_name: str
    tabacco_brand: str
    tabacco_queue: int
    tabacco_weight: int
    note: str

    def get_queue(self):
        return self.tabacco_queue
    
    def set_queue(self, queue: int):
        self.tabacco_queue = queue if queue >= 1 else 1

@dataclass(init = False)
class MixData():
    name: str
    description: str
    tabacco: List[TabaccoComponent]
    created_by: int
    datetime: int


    def __init__(self, name, desctiption, tabacco, created_by, datetime) -> None:
        self.name = name
        self.description = desctiption
        self.created_by = created_by
        self.datetime = datetime
        self.tabacco = []

        for item in tabacco:
            self.tabacco.append(TabaccoComponent(**item))



class Mixes(Basic):
    _id: ObjectId = Field(default_factory = ObjectId, alias = "_id") 
    name: str
    description: str
    tabacco: List[TabaccoComponent]
    created_by: int
    datetime: int

    @classmethod
    async def create_mix(cls, name: str, description: str, tabacco: List[TabaccoComponent], created_by: int, datetime: int):
        pass