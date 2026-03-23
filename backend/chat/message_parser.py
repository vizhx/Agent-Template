"""
LLM-agnostic message parser for assistant responses.
Parses assistant messages into structured content blocks (text and tool calls).
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TextContent:
    """Represents a text content block."""
    type: str = "text"
    content: str = ""
    partial: bool = True


@dataclass
class ToolUse:
    """Represents a tool use content block."""
    type: str = "tool_use"
    name: str = ""
    params: Dict[str, str] = None
    partial: bool = True
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


# Tool names that can appear in assistant messages
TOOL_USE_NAMES = [
    "calculator",
    "current_time",
    "web_search",
    "thinking",
    "complete_task",
    "edit_content",
    "get_current_content",
]

# Parameter names that can appear in tool uses
TOOL_PARAM_NAMES = [
    "expression",
    "format",
    "query",
    "content",
    "summary",
    "newContent",
]


class MessageParser:
    """
    Parser for assistant messages that extracts text content and tool calls.
    This is LLM-agnostic and works with any provider that uses XML-style tool tags.
    """
    
    def __init__(self):
        # Precompute tags for faster lookups
        self.tool_use_open_tags = {f"<{name}>": name for name in TOOL_USE_NAMES}
        self.tool_param_open_tags = {f"<{name}>": name for name in TOOL_PARAM_NAMES}
    
    def parse(self, assistant_message: str) -> List[Dict[str, Any]]:
        """
        Parse an assistant message into content blocks.
        
        Args:
            assistant_message: The raw assistant message string
            
        Returns:
            List of content blocks (text and tool use dictionaries)
        """
        content_blocks = []
        current_text_content_start = 0
        current_text_content: Optional[TextContent] = None
        current_tool_use_start = 0
        current_tool_use: Optional[ToolUse] = None
        current_param_value_start = 0
        current_param_name: Optional[str] = None
        
        length = len(assistant_message)
        
        for i in range(length):
            current_char_index = i
            
            # State: Parsing a Tool Parameter
            if current_tool_use and current_param_name:
                close_tag = f"</{current_param_name}>"
                
                # Check if we've reached the closing tag
                if (current_char_index >= len(close_tag) - 1 and
                    assistant_message.startswith(close_tag, current_char_index - len(close_tag) + 1)):
                    
                    # Extract parameter value
                    value = assistant_message[
                        current_param_value_start:current_char_index - len(close_tag) + 1
                    ].strip()
                    current_tool_use.params[current_param_name] = value
                    current_param_name = None
                else:
                    continue
            
            # State: Parsing a Tool Use (but not a specific parameter)
            if current_tool_use and not current_param_name:
                # Check if starting a new parameter
                started_new_param = False
                for tag, param_name in self.tool_param_open_tags.items():
                    if (current_char_index >= len(tag) - 1 and
                        assistant_message.startswith(tag, current_char_index - len(tag) + 1)):
                        current_param_name = param_name
                        current_param_value_start = current_char_index + 1
                        started_new_param = True
                        break
                
                if started_new_param:
                    continue
                
                # Check if closing the current tool use
                tool_close_tag = f"</{current_tool_use.name}>"
                if (current_char_index >= len(tool_close_tag) - 1 and
                    assistant_message.startswith(tool_close_tag, current_char_index - len(tool_close_tag) + 1)):
                    
                    # Special handling for content parameter in specific tools
                    tool_content_slice = assistant_message[
                        current_tool_use_start:current_char_index - len(tool_close_tag) + 1
                    ]
                    
                    if (current_tool_use.name in ["calculator", "edit_content"] and
                        "<content>" in tool_content_slice):
                        content_start_tag = "<content>"
                        content_end_tag = "</content>"
                        content_start = tool_content_slice.find(content_start_tag)
                        content_end = tool_content_slice.rfind(content_end_tag)
                        
                        if content_start != -1 and content_end != -1 and content_end > content_start:
                            content_value = tool_content_slice[
                                content_start + len(content_start_tag):content_end
                            ].strip()
                            current_tool_use.params["content"] = content_value
                    
                    # Mark tool as complete and add to blocks
                    current_tool_use.partial = False
                    content_blocks.append(self._tool_use_to_dict(current_tool_use))
                    current_tool_use = None
                    current_text_content_start = current_char_index + 1
                    continue
                
                continue
            
            # State: Parsing Text / Looking for Tool Start
            if not current_tool_use:
                # Check if starting a new tool use
                started_new_tool = False
                for tag, tool_name in self.tool_use_open_tags.items():
                    if (current_char_index >= len(tag) - 1 and
                        assistant_message.startswith(tag, current_char_index - len(tag) + 1)):
                        
                        # End current text block if one was active
                        if current_text_content:
                            current_text_content.content = assistant_message[
                                current_text_content_start:current_char_index - len(tag) + 1
                            ].strip()
                            current_text_content.partial = False
                            if current_text_content.content:
                                content_blocks.append(self._text_content_to_dict(current_text_content))
                            current_text_content = None
                        else:
                            # Check for text between last block and this tag
                            potential_text = assistant_message[
                                current_text_content_start:current_char_index - len(tag) + 1
                            ].strip()
                            if potential_text:
                                content_blocks.append({
                                    "type": "text",
                                    "content": potential_text,
                                    "partial": False
                                })
                        
                        # Start new tool use
                        current_tool_use = ToolUse(name=tool_name, partial=True)
                        current_tool_use_start = current_char_index + 1
                        started_new_tool = True
                        break
                
                if started_new_tool:
                    continue
                
                # If not starting a tool, it's text content
                if not current_text_content:
                    current_text_content_start = current_char_index
                    current_text_content = TextContent(partial=True)
        
        # Finalization after loop
        
        # Finalize any open parameter within an open tool use
        if current_tool_use and current_param_name:
            current_tool_use.params[current_param_name] = assistant_message[
                current_param_value_start:
            ].strip()
        
        # Finalize any open tool use
        if current_tool_use:
            content_blocks.append(self._tool_use_to_dict(current_tool_use))
        # Finalize any trailing text content
        elif current_text_content:
            current_text_content.content = assistant_message[
                current_text_content_start:
            ].strip()
            if current_text_content.content:
                content_blocks.append(self._text_content_to_dict(current_text_content))
        
        return content_blocks
    
    def _text_content_to_dict(self, text_content: TextContent) -> Dict[str, Any]:
        """Convert TextContent to dictionary."""
        return {
            "type": text_content.type,
            "content": text_content.content,
            "partial": text_content.partial
        }
    
    def _tool_use_to_dict(self, tool_use: ToolUse) -> Dict[str, Any]:
        """Convert ToolUse to dictionary."""
        return {
            "type": tool_use.type,
            "name": tool_use.name,
            "params": tool_use.params,
            "partial": tool_use.partial
        }


# Global parser instance
message_parser = MessageParser()


def parse_assistant_message(assistant_message: str) -> List[Dict[str, Any]]:
    """
    Parse an assistant message into content blocks.
    
    Args:
        assistant_message: The raw assistant message string
        
    Returns:
        List of content blocks (text and tool use dictionaries)
    """
    return message_parser.parse(assistant_message)