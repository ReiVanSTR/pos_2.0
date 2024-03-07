from typing import Callable, List, Union
from aiogram.types import InlineKeyboardMarkup

class BasicKeyboard:
    def __init__(self, name, prev, next, contains: Union[InlineKeyboardMarkup, Callable]):
        self.name = name # {category}:{subcategory}:[name]
        self.prev = prev
        self.next = next
        self.contains = contains

class BasicMultiKeyboard():
    def __init__(self,name, prev, next, contains: List[BasicKeyboard]) -> None:
        self.name = name # {category}:{subcategory}:[name]
        self.prev = prev
        self.next = next
        self.contains = contains

class BasicKeyboardList:
    root = None
    end = None
    current = None
    
    def insert_root(self, name, contains: Union[InlineKeyboardMarkup, Callable]):
        if self.root == None:
            keyboard = BasicKeyboard(name, None, None, contains)
            self.root = keyboard
            self.end = keyboard
        else:
            keyboard = BasicKeyboard(name, None, self.root, contains)

            self.root.prev = keyboard
            self.root = keyboard
    
    def insert_end(self, name, contains: InlineKeyboardMarkup):
        if self.end == None:
            keyboard = BasicKeyboard(name, None, None, contains)
            self.root = keyboard
            self.end = keyboard
        else:
            keyboard = BasicKeyboard(name, self.end, None, contains)
            self.end.next = keyboard
            self.end = keyboard

    def output(self):
        current = self.root

        while current.next is not None:
            print(current.name)
            current = current.next
        print(current.name)

    def get_current(self):
        if self.root is None:
            return None

        if not self.current:
            self.current = self.root
            return self.current

        return self.current

    def get_next(self):
        if self.root is None:
            return None
        
        if not self.current:
            self.current = self.root
            if self.current.next:
                self.current = self.current.next
                return self.current

            return self.current
        
        if not self.current.next:
            return None

        self.current = self.current.next

        return self.current

    def get_prev(self):
        if self.root is None:
            return None
        
        if not self.current:
            self.current = self.root
            if self.current.prev: 
                self.current = self.current.prev
                return self.current
            return None
        
        if not self.current.prev:
            return None
        
        self.current = self.current.prev

        return self.current
    
    def get_end(self):
        return self.end
    
    def get_root(self):
        return self.root        