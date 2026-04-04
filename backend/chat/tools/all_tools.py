from typing import Dict, Any
from .base import BaseTool, ToolRegistry
from ..content_manager import content_manager

class EditContentTool(BaseTool):
    """
    A tool for editing the global content. Requires user approval.
    """
    def __init__(self):
        super().__init__()
        self.name="edit_content"
        self.description="Edit the global content. This requires user approval."
        self.parameters={
            "type": "object",
            "properties": {
                "newContent": {
                    "type": "string",
                    "description": "The complete new content to replace the existing content."
                }
            },
            "required": ["newContent"]
        }
        self.needs_approval=True
        self.show_preview=True

    async def _show_preview(self, args: Dict, task_id: str):
        """
        Generates a preview of content changes and broadcasts it.
        """
        old_content = content_manager.get_content()
        new_content = args.get("newContent", "")
        await content_manager.broadcast_content_preview(old_content, new_content)

    async def execute(self, args: Dict, task_id: str) -> str:
        new_content = args.get("newContent")
        if new_content is None:
            return "Error: 'newContent' parameter is required."
        
        await content_manager.update_content(new_content)
        return "Content updated successfully."

class GetCurrentContentTool(BaseTool):
    """
    A tool for retrieving the current global content.
    """
    def __init__(self):
        super().__init__()
        self.name="get_current_content"
        self.description="Get the current global content."
        self.parameters={
            "type": "object",
            "properties": {}
        }
        self.needs_approval=False

    async def execute(self, args: Dict, task_id: str) -> str:
        return content_manager.get_content()

class CompleteTaskTool(BaseTool):
    """
    A tool to mark the current task as complete and provide a summary.
    """
    def __init__(self):
        super().__init__()
        self.name="complete_task"
        self.description="Mark the current task as complete and provide a summary of the outcome."
        self.parameters={
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A concise summary of the task's outcome."
                }
            },
            "required": ["summary"]
        }
        self.needs_approval=False
        

    async def execute(self, args: Dict, task_id: str) -> str:
        summary = args.get("summary", "Task completed.")
        # In a real application, you might update the Task model status here
        return f"Task marked as complete: {summary}"


