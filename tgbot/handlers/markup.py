import logging
from inspect import iscoroutinefunction
from typing import Callable, List

class onState():
    def __init__(self, state) -> None:
        self.state = state

    def __call__(self, state):
        return self.state == state
    

class StateKeyboard():
    def __init__(self, filtr: onState, text, keyboard, getter = None, on_call = None) -> None:
        self.filtr = filtr
        self.text = text
        self.keyboard = keyboard
        self.getter = getter
        self.on_call = on_call

    async def __call__(self, state):
        if self.filtr(state):
            if self.on_call:
                if iscoroutinefunction(self.on_call):
                    await self.on_call()
                else:
                    self.on_call()

            _getter_result = None
            if self.getter:
                if iscoroutinefunction(self.getter):
                    _getter_result = await self.getter()

                else:
                    _getter_result = self.getter()

            if iscoroutinefunction(self.keyboard):             
                keyboard = await self.keyboard(_getter_result) if _getter_result else await self.keyboard()
                return {"text":self.text, "keyboard":keyboard}
                         
            keyboard = self.keyboard(_getter_result) if _getter_result else self.keyboard()
            return {"text":self.text, "keyboard":keyboard}
           
        return False
    
class Markups:
    keyboards: List[StateKeyboard] = []
    keys: List[str] = []

    def register(self, key: str, keyboard: StateKeyboard):
        if not key in self.keys:
            self.keys.append(key)
            self.keyboards.append(keyboard)

    async def get_markup(self, state):
        for keyboard in self.keyboards:
            result = await keyboard(state)

            if result:
                return result
            
        return None