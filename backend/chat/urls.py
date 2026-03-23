from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet,
    task_event_stream_view,
    content_event_stream_view
)

# Create a router and register the TaskViewSet
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # Include router URLs (handles list, create, retrieve, destroy, messages, approve-tool)
    path('', include(router.urls)),
    # Custom SSE streaming endpoints
    path('tasks/<str:task_id>/stream/', task_event_stream_view, name='task-event-stream'),
    path('content-stream/', content_event_stream_view, name='content-event-stream'),
]
