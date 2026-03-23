from django.db import models
from django.db.models import UUIDField, CharField, DateTimeField, ForeignKey, CASCADE, BigIntegerField, JSONField, Index
from uuid import uuid4

class Task(models.Model):
    """
    Represents a conversation task/session.
    """
    id = UUIDField(primary_key=True, default=uuid4)
    user_id = CharField(max_length=255, db_index=True)
    title = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['user_id', '-created_at'])
        ]

    def __str__(self):
        return f"Task {self.id} - {self.title}"

class InteractionRecord(models.Model):
    """
    Stores complete interaction data as JSON for a task.
    """
    id = UUIDField(primary_key=True, default=uuid4)
    task = ForeignKey(Task, on_delete=CASCADE, related_name='interactions')
    ts = BigIntegerField()  # Timestamp in milliseconds
    data = JSONField()      # Complete interaction data
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ts']
        indexes = [
            Index(fields=['task', 'ts'])
        ]

    def __str__(self):
        return f"InteractionRecord for Task {self.task.id} at {self.ts}"
