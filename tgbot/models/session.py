from pydantic import Field
from dataclasses import dataclass
from .basic import Basic, ObjectId
from typing import List

class Session(Basic):
    _id: ObjectId = Field(default_factory = ObjectId, alias = "_id") 
    
