import asyncio
import json
import os
from typing import Dict, Any, Set

class ContentManager:
    """
    Manages global content state, persists it to a file, and broadcasts updates.
    """
    def __init__(self, content_file_path: str = "scenic_places.txt"):
        self.content_file_path = content_file_path  # Django runs from backend dir, so no need to add 'backend' prefix
        self.current_content: str = self._load_initial_content()
        self.subscribers: Set[asyncio.Queue] = set() # For SSE streaming

    def _load_initial_content(self) -> str:
        """
        Loads initial content from the specified file.
        """
        if os.path.exists(self.content_file_path):
            with open(self.content_file_path, 'r') as f:
                return f.read()
        return "Initial content: No content file found."

    def get_content(self) -> str:
        """
        Returns the current global content.
        """
        return self.current_content

    async def update_content(self, new_content: str):
        """
        Updates the global content, persists it to file, and broadcasts the update.
        """
        self.current_content = new_content
        with open(self.content_file_path, 'w') as f:
            f.write(new_content)
        
        await self._broadcast_update({
            "type": "content_updated",
            "content": new_content
        })

    async def subscribe(self) -> asyncio.Queue:
        """
        Subscribes a new client to content updates.
        Sends the initial content upon subscription.
        """
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        await queue.put({
            "type": "initial_content",
            "content": self.current_content
        })
        return queue

    async def unsubscribe(self, queue: asyncio.Queue):
        """
        Unsubscribes a client from content updates.
        """
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def broadcast_content_preview(self, old_content: str, new_content: str):
        """
        Broadcasts a content preview event to all subscribers.
        """
        await self._broadcast_update({
            "type": "content_preview",
            "old_content": old_content,
            "new_content": new_content
        })

    async def _broadcast_update(self, update: Dict[str, Any]):
        """
        Internal method to broadcast an update to all active subscribers.
        """
        # Create a copy of the set to avoid issues with modification during iteration
        for queue in list(self.subscribers):
            try:
                await queue.put(update)
            except Exception as e:
                print(f"Error broadcasting to queue: {e}")
                self.subscribers.discard(queue) # Remove broken queues

# Global content manager instance
content_manager = ContentManager()
