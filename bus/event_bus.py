import asyncio
import logging
from typing import Callable, Dict, List, Type
from bus.events import Event

logger = logging.getLogger("EventBus")

class EventBus:
    def __init__(self):
        self._listeners: Dict[Type[Event], List[Callable]] = {}

    def subscribe(self, event_type: Type[Event], listener: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        logger.info(f"Subscribed {listener.__name__} to {event_type.__name__}")

    async def publish(self, event: Event):
        event_type = type(event)
        if event_type in self._listeners:
            tasks = []
            for listener in self._listeners[event_type]:
                if asyncio.iscoroutinefunction(listener):
                    tasks.append(listener(event))
                else:
                    listener(event)
            if tasks:
                await asyncio.gather(*tasks)

event_bus = EventBus()