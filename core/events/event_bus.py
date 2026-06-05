import asyncio
import logging
from typing import Callable, Dict, List, Any
from .event_types import Event, EventType

logger = logging.getLogger("mintuu.events.bus")

class EventBus:
    """Async event bus for pub/sub messaging."""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._queue = asyncio.Queue()
        self._is_running = False
        self._task = None
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe a handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")
        
    async def publish(self, event: Event):
        """Publish an event to the queue."""
        await self._queue.put(event)
        logger.debug(f"Published event: {event.type} ({event.id})")
        
    async def start(self):
        """Start the event processing loop."""
        self._is_running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("Event Bus started.")
        
    async def stop(self):
        """Stop the event processing loop."""
        self._is_running = False
        if self._task:
            self._task.cancel()
        logger.info("Event Bus stopped.")
        
    async def _process_events(self):
        """Continuously process events from the queue."""
        while self._is_running:
            try:
                event = await self._queue.get()
                handlers = self._subscribers.get(event.type, [])
                
                # Execute all handlers concurrently
                tasks = [handler(event) for handler in handlers if asyncio.iscoroutinefunction(handler)]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
