"""
Task class for managing conversations and LLM interactions.
"""
import asyncio
import datetime
import uuid
import time
from typing import AsyncGenerator, Dict, Any, List
from django.conf import settings
from .models import Task as TaskModel, InteractionRecord
from .llm.provider import LLMMessage
from .llm import create_provider
from .llm.prompts import get_system_prompt
from .tools.base import ToolRegistry
from .message_parser import parse_assistant_message


class Task:
    """
    Core task execution class.
    Manages conversation, LLM interaction, and tool execution.
    """
    
    
    def __init__(self, task_id: str, user_id: str, title: str, interaction_record_id: str = None, created_at: datetime.datetime = None, updated_at: datetime.datetime = None):
        self.id = task_id
        self.user_id = user_id
        self.title = title
        self.interaction_record_id = interaction_record_id
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or datetime.datetime.now()
        
        # Use factory to create the LLM provider
        self.llm_provider = create_provider()
        
        self.pending_tool_request: Dict[str, Any] = None  # Stores pending tool call awaiting approval
        self.conversation_history: List[LLMMessage] = []
        self.tool_registry = ToolRegistry()
        self.event_subscribers: List[asyncio.Queue] = []  # Event queue subscribers
        self.is_busy = False
    
    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to task events"""
        queue = asyncio.Queue()
        self.event_subscribers.append(queue)
        return queue
    
    async def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from task events"""
        if queue in self.event_subscribers:
            self.event_subscribers.remove(queue)
    
    async def _broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all subscribers"""
        for queue in self.event_subscribers:
            await queue.put(event)
            
    async def _update_task_status(self, is_busy: bool):
        """Update the is_busy state and broadcast the change."""
        self.is_busy = is_busy
        await self._broadcast_event({
            "type": "task_status",
            "is_busy": is_busy,
            "ts": int(time.time() * 1000)
        })

    async def interrupt(self):
        """Interrupt the current LLM generation stream."""
        await self._update_task_status(False)
        return True
    
    @classmethod
    def create(cls, user_id: str, title: str) -> 'Task':
        """
        Create a new task and save it to the database.
        Creates an empty InteractionRecord to store the conversation.
        
        Args:
            user_id: User ID
            title: Task title
            
        Returns:
            Task instance
        """
        task_model = TaskModel.objects.create(user_id=user_id, title=title)
        
        # Create an empty interaction record for this task
        interaction_record = InteractionRecord.objects.create(
            task=task_model,
            ts=int(time.time() * 1000),
            data={"interactions": []}
        )
        
        return cls(str(task_model.id), user_id, title, str(interaction_record.id), task_model.created_at, task_model.updated_at)
    
    @classmethod
    async def acreate(cls, user_id: str, title: str) -> 'Task':
        """
        Create a new task asynchronously and save to DB.
        """
        task_model = await TaskModel.objects.acreate(user_id=user_id, title=title)
        interaction_record = await InteractionRecord.objects.acreate(
            task=task_model,
            ts=int(time.time() * 1000),
            data={"interactions": []}
        )
        return cls(str(task_model.id), user_id, title, str(interaction_record.id), task_model.created_at, task_model.updated_at)
    
    @classmethod
    async def from_model(cls, task_model: TaskModel) -> 'Task':
        """
        Load a task from a database model and restore conversation history.
        
        Args:
            task_model: TaskModel instance
            
        Returns:
            Task instance with restored conversation history
        """
        # Get the interaction record for this task
        interaction_record = await InteractionRecord.objects.filter(task=task_model).afirst()
        
        interaction_record_id = str(interaction_record.id) if interaction_record else None
        task = cls(str(task_model.id), task_model.user_id, task_model.title, interaction_record_id, task_model.created_at, task_model.updated_at)
        
        # Restore conversation history from interaction record
        if interaction_record and interaction_record.data:
            interactions = interaction_record.data.get("interactions", [])
            
            # Rebuild conversation history from stored interactions
            for interaction in interactions:
                if interaction.get("type") == "user_message":
                    task.conversation_history.append(
                        LLMMessage(role="user", content=interaction.get("content", ""))
                    )
                elif interaction.get("type") == "assistant_message":
                    task.conversation_history.append(
                        LLMMessage(role="assistant", content=interaction.get("content", ""))
                    )
        
        return task
    
    async def process_user_message(self, content: str):
        """
        Process user message and broadcast events.
        
        Args:
            content: User message content
        """
        if self.is_busy:
            await self._broadcast_event({
                "type": "error",
                "error": "Task is already busy processing."
            })
            return
            
        await self._update_task_status(True)
        
        # Add user message to conversation
        user_msg = LLMMessage(role="user", content=content)
        self.conversation_history.append(user_msg)
        
        # Save user interaction
        await self._save_interaction({
            "type": "user_message",
            "content": content,
            "ts": int(time.time() * 1000)
        })
        
        # Broadcast user message event
        await self._broadcast_event({
            "type": "user_message",
            "content": content,
            "ts": int(time.time() * 1000)
        })
        
        # Start the agent loop
        await self.start_agent_loop()
    
    async def start_agent_loop(self):
        """
        Start the agent loop that continues streaming until completion or approval request.
        This can be called after user messages or after tool approval/rejection.
        
        Yields:
            Dictionary chunks containing response data
        """
        try:
            # Stream LLM response, continuing after tool executions
            # The loop continues until complete_task tool or approval request
            while True:
                should_stop = False
                
                async for chunk in self.stream_llm_response():
                    await self._broadcast_event(chunk)
                    
                    chunk_type = chunk.get("type")
                    
                    # Stop completely if tool needs approval or task is complete
                    if chunk_type == "tool_approval_request":
                        should_stop = True
                        break
                        
                    if chunk_type == "assistant_complete":
                        should_stop = True
                    
                    # If tool was executed, break to restart stream (unless it's complete_task)
                    if chunk_type == "tool_executed":
                        if chunk.get("is_complete"):
                            should_stop = True
                        break
                
                # Exit loop if we should stop completely
                if should_stop:
                    break
                    
        except Exception as error:
            print("error occurred", error)
            await self._broadcast_event({
                "type": "error",
                "error": str(error)
            })
        finally:
            await self._update_task_status(False)
    
    async def stream_llm_response(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream LLM response with tool call handling.
        Parses assistant messages into content blocks and handles tools.
        
        Yields:
            Dictionary chunks containing response data
        """
        accumulated_content = ""
        
        
            
        system_prompt = get_system_prompt()
        async for chunk in self.llm_provider.generate_streaming_response(
            messages=self.conversation_history,
            system_prompt=system_prompt
        ):
            if not self.is_busy:
                parsed_blocks = parse_assistant_message(accumulated_content)
                assistant_msg = LLMMessage(role="assistant", content=accumulated_content)
                self.conversation_history.append(assistant_msg)
                await self._save_interaction({
                    "type": "assistant_message",
                    "content": accumulated_content,
                    "parsed_content": parsed_blocks,
                    "ts": int(time.time() * 1000)
                })
                yield {
                    "type": "assistant_complete",
                    "content": accumulated_content,
                    "parsed_content": parsed_blocks
                }
                break

            accumulated_content += chunk.content
            
            # Parse the accumulated content to get structured blocks
            parsed_blocks = parse_assistant_message(accumulated_content)
            
            # Find first complete tool and discard any blocks after it
            tool_block = None
            for i, block in enumerate(parsed_blocks):
                if block.get("type") == "tool_use" and not block.get("partial", True):
                    tool_block = block
                    parsed_blocks = parsed_blocks[:i + 1]
                    break
            
            # Handle tool call if present
            if tool_block:
                yield {
                    "type": "assistant_chunk",
                    "content": chunk.content,
                    "parsed_content": parsed_blocks,
                    "is_complete": False
                }

                tool_call = {
                    "id": f"tool_{int(time.time() * 1000)}",
                    "name": tool_block["name"],
                    "input": tool_block["params"]
                }
                
                # Check if tool needs approval
                tool = self.tool_registry.get_tool(tool_block["name"])
                if tool and tool.requires_approval():
                    # Show preview if available
                    if tool.show_preview:
                        await tool.preview(tool_call["input"], task_id=self.id)
                    
                    # Store the pending tool request
                    self.pending_tool_request = {
                        "tool_call": tool_call,
                        "tool_block": tool_block,
                        "accumulated_content": accumulated_content,
                        "parsed_blocks": parsed_blocks
                    }
                    # Add assistant message to history before breaking
                    assistant_msg = LLMMessage(role="assistant", content=accumulated_content)
                    self.conversation_history.append(assistant_msg)
                    # Save assistant interaction
                    await self._save_interaction({
                        "type": "assistant_message",
                        "content": accumulated_content,
                        "parsed_content": parsed_blocks,
                        "ts": int(time.time() * 1000)
                    })

                    # Yield approval request event and break
                    # Frontend will handle approval and send response via separate endpoint
                    yield {
                        "type": "tool_approval_request",
                        "tool_call": tool_call
                    }
                    
                    break
                
                # Execute tool if no approval needed
                tool_result = await self.execute_tool(tool_call)
                
                # Add assistant message with tool call to history
                assistant_msg = LLMMessage(role="assistant", content=accumulated_content)
                self.conversation_history.append(assistant_msg)
                
                # Save assistant interaction
                await self._save_interaction({
                    "type": "assistant_message",
                    "content": accumulated_content,
                    "parsed_content": parsed_blocks,
                    "ts": int(time.time() * 1000)
                })
                
                # Check if this is the complete_task tool
                is_complete_task = tool_block["name"] == "complete_task"
                
                # Add tool result to conversation history (unless it's complete_task)
                if not is_complete_task:
                    tool_result_msg = LLMMessage(
                        role="user",
                        content=f"Tool '{tool_block['name']}' result: {tool_result}"
                    )
                    self.conversation_history.append(tool_result_msg)
                
                # Save tool result interaction
                await self._save_interaction({
                    "type": "tool_result",
                    "tool_name": tool_block["name"],
                    "result": tool_result,
                    "ts": int(time.time() * 1000)
                })
                
                # Yield tool execution event
                yield {
                    "type": "tool_executed",
                    "tool_name": tool_block["name"],
                    "result": tool_result,
                    "is_complete": is_complete_task
                }
                
                # Break to reset stream and continue with tool result
                break

            
            # Yield parsed content blocks
            yield {
                "type": "assistant_chunk",
                "content": chunk.content,
                "parsed_content": parsed_blocks,
                "is_complete": False
            }
            
            if chunk.is_complete:
                # Parse final message
                parsed_blocks = parse_assistant_message(accumulated_content)
                
                # Add assistant message to history
                assistant_msg = LLMMessage(role="assistant", content=accumulated_content)
                self.conversation_history.append(assistant_msg)
                
                # Save assistant interaction with parsed blocks
                await self._save_interaction({
                    "type": "assistant_message",
                    "content": accumulated_content,
                    "parsed_content": parsed_blocks,
                    "ts": int(time.time() * 1000)
                })
                yield {
                    "type": "assistant_complete",
                    "content": accumulated_content,
                    "parsed_content": parsed_blocks
                }
                break
                     
    async def handle_tool_approval(self, tool_call_id: str, approved: bool):
        """
        Handle tool approval/rejection from frontend.
        Executes the tool if approved, then restarts the agent loop.
        Broadcasts events instead of returning them.
        
        Args:
            tool_call_id: Tool call ID
            approved: Whether the tool was approved
        """
        if self.is_busy:
            await self._broadcast_event({
                "type": "error",
                "error": "Task is already busy processing."
            })
            return
            
        await self._update_task_status(True)
        
        if not self.pending_tool_request:
            await self._broadcast_event({
                "type": "error",
                "error": "Tool call not found"
            })
            return
        
        stored_tool_call = self.pending_tool_request.get("tool_call", {})
        if stored_tool_call.get("id") != tool_call_id:
            print("stored id does not match received id")
            await self._broadcast_event({
                "type": "error",
                "error": "Tool call not found"
            })
            return
        
        tool_block = self.pending_tool_request.get("tool_block")
        
        if approved:
            # Execute the approved tool
            print("EXECUTING TOOL", tool_block)
            tool_result = await self.execute_tool(stored_tool_call)
            print("Tool Result", tool_result)
            # Check if this is the complete_task tool
            is_complete_task = tool_block["name"] == "complete_task"
            
            # Add tool result to conversation history (unless it's complete_task)
            if not is_complete_task:
                tool_result_msg = LLMMessage(
                    role="user",
                    content=f"Tool '{tool_block['name']}' result: {tool_result}"
                )
                self.conversation_history.append(tool_result_msg)
            
            # Save tool result interaction
            await self._save_interaction({
                "type": "tool_result",
                "tool_name": tool_block["name"],
                "result": tool_result,
                "approved": True,
                "ts": int(time.time() * 1000)
            })
            
            # Broadcast tool executed event
            await self._broadcast_event({
                "type": "tool_executed",
                "tool_name": tool_block["name"],
                "result": tool_result,
                "is_complete": is_complete_task
            })
        else:
            # Tool was rejected - add rejection to conversation history
            rejection_msg = LLMMessage(
                role="user",
                content=f"Tool '{tool_block['name']}' was rejected by the user. Please proceed without executing this tool."
            )
            self.conversation_history.append(rejection_msg)
            
            # Save rejection interaction
            await self._save_interaction({
                "type": "tool_result",
                "tool_name": tool_block["name"],
                "result": "Tool rejected by user",
                "approved": False,
                "ts": int(time.time() * 1000)
            })
            
        # Clear the pending tool request
        self.pending_tool_request = None
        
        # Continue the agent loop
        await self.start_agent_loop()
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """
        Execute a tool call (called after approval if needed).
        
        Args:
            tool_call: Tool call dictionary with name and input
            
        Returns:
            Tool execution result
        """
        tool_name = tool_call.get("name")
        tool_input = tool_call.get("input", {})
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            # Pass task_id to the tool execution
            result = await tool.execute(tool_input, task_id=self.id)
            return result
        except Exception as error:
            return f"Error executing tool: {str(error)}"
    
    async def _save_interaction(self, data: Dict[str, Any]) -> None:
        """
        Append an interaction to the existing InteractionRecord.
        
        Args:
            data: Interaction data to append
        """
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
            
        if not self.interaction_record_id:
            # If no interaction record exists, create one
            task_model = await TaskModel.objects.aget(id=self.id)
            interaction_record = await InteractionRecord.objects.acreate(
                task=task_model,
                ts=int(time.time() * 1000),
                data={"interactions": [data]}
            )
            self.interaction_record_id = str(interaction_record.id)
        else:
            # Append to existing interaction record
            interaction_record = await InteractionRecord.objects.aget(id=self.interaction_record_id)
            interactions = interaction_record.data.get("interactions", [])
            interactions.append(data)
            interaction_record.data = {"interactions": interactions}
            interaction_record.ts = data.get("ts", int(time.time() * 1000))
            await interaction_record.asave()
    
    async def get_interactions(self) -> List[Dict[str, Any]]:
        """
        Get all interactions from the interaction record.
        
        Returns:
            List of interaction dictionaries
        """
        if not self.interaction_record_id:
            return []
        
        try:
            interaction_record = await InteractionRecord.objects.aget(id=self.interaction_record_id)
            return interaction_record.data.get("interactions", [])
        except InteractionRecord.DoesNotExist:
            return []

    async def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get all interactions formatted as frontend Messages with blocks.
        """
        interactions = await self.get_interactions()
        messages = []
        last_assistant_msg = None
        
        for interaction in interactions:
            msg_id = interaction.get("id") or str(uuid.uuid4())
            ts_val = interaction.get("ts", time.time() * 1000)
            try:
                ts = datetime.datetime.fromtimestamp(ts_val / 1000.0).isoformat()
            except Exception:
                ts = datetime.datetime.now().isoformat()
            
            if interaction["type"] == "user_message":
                messages.append({
                    "id": msg_id,
                    "sender": "user",
                    "timestamp": ts,
                    "blocks": [{
                        "type": "text",
                        "content": interaction.get("content", "")
                    }]
                })
                last_assistant_msg = None
            
            elif interaction["type"] == "assistant_message":
                blocks = []
                parsed_content = interaction.get("parsed_content", [])
                for block in parsed_content:
                    if block["type"] == "text":
                        blocks.append({
                            "type": "text",
                            "content": block.get("content", block.get("text", ""))
                        })
                    elif block["type"] == "tool_use":
                        blocks.append({
                            "type": "tool_use",
                            "name": block.get("name", ""),
                            "params": block.get("params", {}),
                            "partial": block.get("partial", False),
                            "status": "pending"
                        })
                
                msg = {
                    "id": msg_id,
                    "sender": "agent",
                    "timestamp": ts,
                    "blocks": blocks
                }
                messages.append(msg)
                last_assistant_msg = msg
            
            elif interaction["type"] == "tool_result":
                # Update the status and result in the corresponding tool block of the last assistant message
                if last_assistant_msg:
                    for block in last_assistant_msg["blocks"]:
                        if block["type"] == "tool_use" and block["name"] == interaction.get("tool_name") and block.get("status") == "pending":
                            block["status"] = "executed"
                            block["result"] = str(interaction.get("result", ""))
                            break
        
        return messages
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "status": "active",
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at),
            "messages": [] # Populated by async calls if needed, otherwise empty for list views
        }