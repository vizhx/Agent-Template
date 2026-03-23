import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import type { Task, Message, TaskEvent } from '../types';
import * as taskService from '../services/taskService';
import { connectToTaskUpdates } from '../services/sseService';

interface TaskState {
    currentTask: Task | null;
    isLoading: boolean;
    error: string | null;
    pendingToolApproval: {
        toolCallId: string;
        toolName: string;
        input: Record<string, unknown>;
    } | null;
    currentAgentMessageId: string | null;

    // Actions
    createTask: (title: string) => Promise<void>;
    loadTask: (taskId: string) => Promise<void>;
    deleteTask: (taskId: string) => Promise<void>;
    sendMessage: (content: string) => Promise<void>;
    syncWithBackend: () => Promise<void>;
    loadTasks: () => Promise<Task[]>;
    approveToolCall: (toolCallId: string, approved: boolean) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set, get) => ({
    currentTask: null,
    isLoading: false,
    error: null,
    pendingToolApproval: null,
    currentAgentMessageId: null,

    createTask: async (title: string) => {
        set({ isLoading: true, error: null });
        try {
            const task = await taskService.createTask(title);
            set({ currentTask: task, isLoading: false });
            localStorage.setItem('currentTask', JSON.stringify(task));

            // Connect to SSE
            connectToTaskUpdates(task.id, (event) => {
                const data = JSON.parse(event.data);
                handleTaskEvent(data, set, get);
            });
        } catch (error: any) {
            set({ error: error.message, isLoading: false });
        }
    },

    loadTask: async (taskId: string) => {
        set({ isLoading: true, error: null });
        try {
            const task = await taskService.getTask(taskId);
            set({ currentTask: task, isLoading: false });
            localStorage.setItem('currentTask', JSON.stringify(task));

            // Connect to SSE
            connectToTaskUpdates(task.id, (event) => {
                const data = JSON.parse(event.data);
                handleTaskEvent(data, set, get);
            });
        } catch (error: any) {
            set({ error: error.message, isLoading: false });
        }
    },

    deleteTask: async (taskId: string) => {
        console.warn('deleteTask not implemented', taskId);
        // Implementation for delete task
        set({ currentTask: null });
        localStorage.removeItem('currentTask');
    },

    sendMessage: async (content: string) => {
        const { currentTask } = get();
        if (!currentTask) return;

        const userMessage: Message = {
            id: uuidv4(),
            task_id: currentTask.id,
            sender: 'user',
            content,
            timestamp: new Date().toISOString(),
        };

        set((state) => ({
            currentTask: state.currentTask
                ? { ...state.currentTask, messages: [...state.currentTask.messages, userMessage] }
                : null,
        }));

        try {
            await taskService.sendMessageToTask(content, currentTask.id);
        } catch (error: any) {
            set({ error: error.message });
        }
    },

    syncWithBackend: async () => {
        const savedTask = localStorage.getItem('currentTask');
        if (savedTask) {
            const task = JSON.parse(savedTask);
            try {
                const refreshedTask = await taskService.getTask(task.id);
                // Transform messages if needed
                const messages = refreshedTask.messages;
                set({ currentTask: { ...refreshedTask, messages } });

                connectToTaskUpdates(task.id, (event) => {
                    const data = JSON.parse(event.data);
                    handleTaskEvent(data, set, get);
                });
            } catch (error) {
                console.error('Failed to sync task:', error);
                localStorage.removeItem('currentTask');
            }
        }
    },

    loadTasks: async () => {
        try {
            const tasks = await taskService.getUserTasks('user-1');
            // Sort by most recent and return max 3
            return tasks
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                .slice(0, 3);
        } catch (error) {
            console.error('Failed to load tasks:', error);
            return [];
        }
    },

    approveToolCall: async (toolCallId: string, approved: boolean) => {
        const { currentTask } = get();
        if (!currentTask) return;

        set({ pendingToolApproval: null });
        try {
            await taskService.approveToolCall(currentTask.id, toolCallId, approved);
        } catch (error: any) {
            set({ error: error.message });
        }
    },
}));

const handleTaskEvent = (event: TaskEvent, set: any, get: any) => {
    const { currentTask, currentAgentMessageId } = get();
    if (!currentTask) return;

    switch (event.type) {
        case 'assistant_chunk':
            if (currentAgentMessageId) {
                // Update existing message
                set((state: TaskState) => ({
                    currentTask: state.currentTask ? {
                        ...state.currentTask,
                        messages: state.currentTask.messages.map(msg =>
                            msg.id === currentAgentMessageId
                                ? { ...msg, content: msg.content + event.payload.content }
                                : msg
                        )
                    } : null
                }));
            } else {
                // Create new message
                const newMessage: Message = {
                    id: uuidv4(),
                    task_id: currentTask.id,
                    sender: 'agent',
                    content: event.payload.content,
                    timestamp: new Date().toISOString(),
                };
                set((state: TaskState) => ({
                    currentAgentMessageId: newMessage.id,
                    currentTask: state.currentTask ? {
                        ...state.currentTask,
                        messages: [...state.currentTask.messages, newMessage]
                    } : null
                }));
            }
            break;

        case 'assistant_complete':
            set({ currentAgentMessageId: null });
            break;

        case 'tool_approval_request':
            set({
                pendingToolApproval: {
                    toolCallId: event.payload.tool_call_id,
                    toolName: event.payload.tool_name,
                    input: event.payload.tool_args,
                }
            });
            break;

        case 'tool_executed':
            // Handle tool execution result display if needed
            break;

        case 'error':
            set({ error: event.payload.message });
            break;
    }
};
