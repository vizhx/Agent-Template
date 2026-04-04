from typing import Optional
from ...tools.base import ToolRegistry

def get_system_prompt(base_prompt: Optional[str] = None) -> str:
    """
    Builds the system prompt for the LLM, including tool descriptions and usage guidelines.
    """
    tool_registry = ToolRegistry()
    tools = tool_registry.get_all_tools().values() # Get all tool instances

    tool_descriptions = """Inorder to call any tool, Follow the below rules:
    1. You MUST use the exact XML tags defined below. Do NOT use JSON or any other format.
    2. Always include both the opening and closing tags for the tool and its parameters.
    3. The root of the xml should be the tool name, and the parameters should be the child elements of the root element.
    4. You can ONLY call ONE tool at a time. Never attempt to combine multiple tools in a single response block. 
    Stop your response immediately after the closing tag and  wait for the user to respond with the tool result.
    Below is the format:
    <tool_name>
    <param1_name>param1_value</param1_name>
    <param2_name>param2_value</param2_name>
    ... 
    </tool_name>
    
    """
    if tools:
        tool_descriptions += "You have access to the following tools:\n"
        for tool in tools:
            tool_dict = tool.to_tool_dict()
            tool_descriptions += f"<{tool_dict['tool_schema']['name']}>\n"
            tool_descriptions += f"  <description>{tool_dict['tool_schema']['description']}</description>\n"
            
            params = tool_dict['tool_schema']['input_schema'].get('properties', {})
            for param_name, param_info in params.items():
                tool_descriptions += f"  <{param_name}>[{param_info.get('description', '')}]</{param_name}>\n"
            
            tool_descriptions += f"</{tool_dict['tool_schema']['name']}>\n\n"

        

    default_base_prompt = (
        "You are a helpful AI assistant, who is tasked with helping the user with the creation of a document. "
        "You can edit the document content using the `edit_content` tool. "
        "You can also retrieve the current document content using the `get_current_content` tool. "
        "Always respond in markdown format."
    )

    final_prompt = base_prompt if base_prompt else default_base_prompt
    final_prompt += tool_descriptions
    return final_prompt
