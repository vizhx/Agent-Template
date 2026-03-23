"""
Controller class for managing task lifecycle and coordinating between frontend and Task instances.
"""
from typing import Dict, Any
from .models import Task as TaskModel
from .task import Task


class Controller:
    """
    Manages task lifecycle and coordinates between frontend and Task instances.
    Simplified from the original multi-controller architecture.
    """
    
    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
    
    def create_task(self, user_id: str, title: str) -> Dict[str, Any]:
        """
        Create a new task and return its details.
        
        Args:
            user_id: User ID
            title: Task title
            
        Returns:
            Dictionary with task details
        """
        task = Task.create(user_id, title)
        self.active_tasks[task.id] = task
        return task.to_dict()
    
    async def get_task(self, task_id: str) -> Task:
        """
        Retrieve a task by ID, loading from DB if not in memory.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task instance
        """
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Load from database
        task_model = await TaskModel.objects.aget(id=task_id)
        task = await Task.from_model(task_model)
        self.active_tasks[task_id] = task
        return task
    
    async def process_message_async(self, task_id: str, message: str):
        """
        Process a message in the background and broadcast events via task queue.
        
        Args:
            task_id: Task ID
            message: User message
        """
        task = await self.get_task(task_id)
        await task.process_user_message(message)
    
    async def approve_tool_async(self, task_id: str, tool_call_id: str, approved: bool):
        """
        Approve or reject a tool call in the background and broadcast events via task queue.
        
        Args:
            task_id: Task ID
            tool_call_id: Tool call ID
            approved: Whether the tool was approved
        """
        task = await self.get_task(task_id)
        await task.handle_tool_approval(tool_call_id, approved)
    
    
    async def get_tasks_for_user(self, user_id: str) -> list:
        """
        Get all tasks for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        async for task_model in TaskModel.objects.filter(user_id=user_id):
            tasks.append({
                "id": str(task_model.id),
                "user_id": task_model.user_id,
                "title": task_model.title,
                "created_at": task_model.created_at.isoformat(),
                "updated_at": task_model.updated_at.isoformat()
            })
        return tasks
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # Delete from database
            await TaskModel.objects.filter(id=task_id).adelete()
            return True
        except Exception:
            return False


# Global controller instance
controller = Controller()