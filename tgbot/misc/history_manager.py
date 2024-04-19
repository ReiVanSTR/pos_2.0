import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import HistoryManager
from aiogram.fsm.state import State
from typing import Any, Dict, Optional

class Manager(HistoryManager):

    async def goto(self, go_to: State, push: bool = False):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])

        _state_record = history[-1]
        _state_data = _state_record.get("data")
        _current_state = _state_record.get("state")

        while _current_state != go_to.state:
            history.pop()
            _current_state = history[-1]["state"]

        await self._history_state.update_data(history=history)

        if push:
            self.update(_state_data)

        await self._state.set_state(_current_state)
    
    async def update(self, data):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])
        if not history:
            return None
        record_data = history[-1]["data"]
        record_data.update(data)
        await self._history_state.update_data(history=history)

    async def push(self, state: Optional[str], data: Dict[str, Any] = {}, start_data: Dict[str, Any] = None, push: bool = False):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])

        if len(history) > self._size:
            history = history[-self._size :]
        
        if start_data:
            data.update(start_data)
        
        if push:
            record_data = history[-1]["data"]
            data.update(record_data)

        history.append({"state": state, "data": data})

        await self._history_state.update_data(history = history)
        await self._state.set_state(state)

    async def get_data(self, key: Optional[str], state: Optional[State] = None):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])
        if state:
            for record in history:
                if record["state"] == state.state:
                    return record["data"].get(key)
                
        record_data = history[-1]["data"]

        return record_data.get(key)
    
    
    async def update_data(self, key, value):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])

        record_data = history[-1]["data"]
        record_data[key] = value
        await self._history_state.update_data(history=history)
    
    async def get_all_data(self):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])

        record_data = history[-1]["data"]

        return record_data
    
    async def push_data(self, state: State, data: Dict[str, Any], key: Optional[str] = None, update_dict = False):
        history_data = await self._history_state.get_data()
        history = history_data.setdefault("history", [])

        for record in history:
            if record["state"] == state.state:
                if key and update_dict:
                        if isinstance(record["data"][key], dict):
                            record["data"][key].update(data)
                            await self._history_state.update_data(history=history)
                            return True
                        return False
                if key:
                    record["data"][key] = data
                    await self._history_state.update_data(history=history)
                    return True
                    
                    
                record["data"].update(data)
                await self._history_state.update_data(history=history)