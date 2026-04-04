import asyncio
import json
from django.http import StreamingHttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from adrf.viewsets import ViewSet
from adrf.decorators import api_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .controller import controller
from .content_manager import content_manager


@method_decorator(csrf_exempt, name='dispatch')
class TaskViewSet(ViewSet):
    """
    Unified ViewSet for all task-related operations.
    Handles listing, creating, retrieving, deleting tasks, as well as messages and tool approvals.
    """
    
    async def list(self, request: HttpRequest):
        """List all tasks for a user."""
        user_id = request.GET.get('user_id', 'user-1')
        tasks = await controller.get_tasks_for_user(user_id)
        return Response(tasks)
    
    async def create(self, request: HttpRequest):
        """Create a new task."""
        user_id = request.data.get('userId', 'user-1')
        title = request.data.get('title')
        if not title:
            return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        task_data = await controller.create_task(user_id, title)
        return Response(task_data, status=status.HTTP_201_CREATED)
    
    async def retrieve(self, request: HttpRequest, pk: str = None):
        """Retrieve a specific task."""
        try:
            task = await controller.get_task(pk)
            messages = await task.get_messages()
            task_data = task.to_dict()
            task_data["messages"] = messages
            return Response(task_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    async def destroy(self, request: HttpRequest, pk: str = None):
        """Delete a specific task."""
        success = await controller.delete_task(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Task not found or could not be deleted"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    async def messages(self, request: HttpRequest, pk: str = None):
        """Send a message to a task."""
        content = request.data.get('content')
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asyncio.create_task(controller.process_message_async(pk, content))
            return Response({"status": "message processing started"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='approve-tool')
    async def approve_tool(self, request: HttpRequest, pk: str = None):
        """Approve or reject a tool call for a specific task."""
        tool_call_id = request.data.get('toolCallId')
        approved = request.data.get('approved')
        
        if not tool_call_id or approved is None:
            return Response({"error": "toolCallId and approved status are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asyncio.create_task(controller.approve_tool_async(pk, tool_call_id, approved))
            return Response({"status": "tool approval processed"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    async def interrupt(self, request: HttpRequest, pk: str = None):
        """Interrupt the agent generation for a specific task."""
        try:
            success = await controller.interrupt_task_async(pk)
            return Response({"status": "interrupted" if success else "failed"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_http_methods(["GET"])
async def task_event_stream_view(request: HttpRequest, task_id: str):
    """
    SSE endpoint for streaming events related to a specific task.
    Uses plain Django view to bypass DRF content negotiation.
    """
    async def event_stream():
        """Async generator for streaming task events."""
        queue = None
        try:
            # Get task and subscribe
            task = await controller.get_task(task_id)
            queue = await task.subscribe()
            
            while True:
                update = await queue.get()
                yield f"data: {json.dumps(update)}\n\n"

        except asyncio.CancelledError:
            if queue:
                task = await controller.get_task(task_id)
                await task.unsubscribe(queue)
        except Exception as e:
            print(f"Error in SSE stream for task {task_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            if queue:
                task = await controller.get_task(task_id)
                await task.unsubscribe(queue)
            print(f"SSE stream for task {task_id} closed.")
    
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable buffering for nginx
    return response

@require_http_methods(["GET"])
async def content_event_stream_view(request: HttpRequest):
    """
    SSE endpoint for streaming global content updates.
    Uses plain Django view to bypass DRF content negotiation.
    """
    async def event_stream():
        """Synchronous generator that wraps async operations."""
        queue = None
        try:
            # Subscribe to content manager
            queue = await content_manager.subscribe()
            
            while True:
                update = await queue.get()
                yield f"data: {json.dumps(update)}\n\n"

        except asyncio.CancelledError:
            await content_manager.unsubscribe(queue)
        except Exception as e:
            print(f"Error in SSE content stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            if queue:
                content_manager.unsubscribe(queue)
            print("SSE content stream closed.")
    
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable buffering for nginx
    return response
