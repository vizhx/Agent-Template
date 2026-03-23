from typing import Optional
from ...tools.base import ToolRegistry

def get_system_prompt(base_prompt: Optional[str] = None) -> str:
    """
    Builds the system prompt for the LLM, including tool descriptions and usage guidelines.
    """
    tool_registry = ToolRegistry()
    tools = tool_registry.get_all_tools().values() # Get all tool instances

    tool_descriptions = ""
    if tools:
        tool_descriptions = "\n\nYou have access to the following tools:\n"
        for tool in tools:
            tool_dict = tool.to_tool_dict() # Use the new method
            tool_descriptions += f"<tool_description>\n"
            tool_descriptions += f"<tool_name>{tool_dict['tool_schema']['name']}</tool_name>\n"
            tool_descriptions += f"<description>{tool_dict['tool_schema']['description']}</description>\n"
            tool_descriptions += f"<parameters>\n"
            tool_descriptions += f"{tool_dict['tool_schema']['input_schema']}\n"
            tool_descriptions += f"</parameters>\n"
            tool_descriptions += f"</tool_description>\n"

        tool_descriptions += (
            "\n\n"
            "You can use tools by enclosing a tool_code block in <tool_code> and </tool_code> tags.\n"
            "Inside the tool_code block, use <tool_name> and <parameters> tags.\n"
            "The parameters should be a JSON object with keys matching the tool's input_schema.\n"
            "Example:\n"
            "<tool_code>\n"
            "<tool_name>tool_name_here</tool_name>\n"
            "<parameters>\n"
            "{{ \"param1\": \"value1\", \"param2\": \"value2\" }}\n"
            "</parameters>\n"
            "</tool_code>\n"
            "\n"
            "You must use the `complete_task` tool when you have finished the task and have a final answer or result for the user. "
            "The `complete_task` tool takes a `summary` parameter which should be a concise summary of the task's outcome.\n"
            "Example:\n"
            "<tool_code>\n"
            "<tool_name>complete_task</tool_name>\n"
            "<parameters>\n"
            "{{ \"summary\": \"The task is complete. Here is the final result.\" }}\n"
            "</parameters>\n"
            "</tool_code>\n"
        )

    default_base_prompt = (
        "You are a helpful AI assistant, who is tasked with helping the user with the creation of a document. "
        "You can edit the document content using the `edit_content` tool. "
        "You can also retrieve the current document content using the `get_current_content` tool. "
        "Always respond in markdown format."
    )

    final_prompt = base_prompt if base_prompt else default_base_prompt
    final_prompt += tool_descriptions

    return final_prompt
