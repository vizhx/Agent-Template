from .all_tools import EditContentTool, GetCurrentContentTool, CompleteTaskTool
from .base import tool_registry

# Register all tools
def register_tools():
    """
    Registers all tools with the tool registry.
    Function called once at application startup
    """
    tool_registry.register_tool(EditContentTool())
    tool_registry.register_tool(GetCurrentContentTool())
    tool_registry.register_tool(CompleteTaskTool()) 

__all__ = [
    "tool_registry",
    "register_tools",
    "EditContentTool",
    "GetCurrentContentTool",
    "CompleteTaskTool"
]
