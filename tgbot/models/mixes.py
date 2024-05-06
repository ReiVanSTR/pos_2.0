from pydantic import Field
from typing import Union
from dataclasses import dataclass
from .basic import Basic, ObjectId
from typing import List

class Mixes(Basic):

    @classmethod
    async def create_mix(cls, name):
        pass