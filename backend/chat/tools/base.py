from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.parameters: Dict[str, Any] = {}
        self.needs_approval: bool = False
        self.show_preview: bool = False


    def requires_approval(self) -> bool:
        """Indicates if the tool requires explicit user approval before execution."""
        return self.needs_approval

    async def preview(self, args: Dict, task_id: str) -> Any:
        """
        Generates a preview of the tool's effect without actually executing it.
        This method is optional and only called if the concrete class implements `_show_preview`.
        """
        if hasattr(self, '_show_preview'):
            return await getattr(self, '_show_preview')(args, task_id)
        return None

    @abstractmethod
    async def execute(self, args: Dict, task_id: str) -> str:
        """
        Executes the tool with the given arguments.
        Must be implemented by concrete tool classes.
        """
        pass

    def to_tool_dict(self) -> Dict:
        """
        Converts the tool definition to Anthropic's tool_schema format.
        """
        return {
            "tool_schema": {
                "name": self.name,
                "description": self.description,
                "input_schema": self.parameters,
            }
        }

class ToolRegistry:
    """
    Singleton registry for managing all available tools.
    """
    _instance: Optional['ToolRegistry'] = None
    tools: Dict[str, BaseTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.tools = {} # Initialize tools dictionary
        return cls._instance

    def register_tool(self, tool: BaseTool):
        """Registers a tool with the registry."""
        if not isinstance(tool, BaseTool):
            raise TypeError("Only instances of BaseTool can be registered.")
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieves a tool by its name."""
        return self.tools.get(name)

    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Returns a dictionary of all registered tools."""
        return self.tools

    def has_tool(self, name: str) -> bool:
        """Checks if a tool with the given name is registered."""
        return name in self.tools

    def remove_tool(self, name: str) -> bool:
        """Removes a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            return True
        return False

    def clear_tools(self):
        """Clears all registered tools."""
        self.tools = {}

tool_registry = ToolRegistry()

