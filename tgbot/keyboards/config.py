from dataclasses import dataclass
from typing import List, Dict

cost_menu = [
    {"name":"Standart", "cost":80},
    {"name":"Premium", "cost":100},
    {"name":"Stuff", "cost":40},
    {"name":"R/W Chief", "cost":0},
]


@dataclass
class CostMenu:
    cost_list: List[Dict[str, int]]


@dataclass
class KeyboardsConfig():
    cost_menu: CostMenu = None