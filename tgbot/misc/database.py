from email.policy import strict
from tracemalloc import stop
from urllib import response
from redis import Redis
from typing import List
from dataclasses import dataclass

rc = Redis(db = 0)


@dataclass
class Brend:
    brand_name: str
    type: str
    contains: List


class DB:
    def __init__(self, rc: Redis):
        self.rc = rc
    
    def get_all_brands(self, type: str) -> List[str]:
        brands = self.rc.json().get("storage", "$.brands")[0]
        response = []
        for brand in brands:
            if brand["type"] == type:
                response.append(brand["brand_name"])

        return response