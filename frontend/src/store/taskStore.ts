import { create, type StoreApi } from 'zustand';
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
    interruptTask: (taskId: string) => Promise<void>;
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
        } catch (error: unknown) {
            set({ error: error instanceof Error ? error.message : String(error), isLoading: false });
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
        } catch (error: unknown) {
            set({ error: error instanceof Error ? error.message : String(error), isLoading: false });
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
            sender: 'user',
            timestamp: new Date().toISOString(),
            blocks: [{ type: 'text', content }]
        };

        set((state) => ({
            currentTask: state.currentTask
                ? { ...state.currentTask, is_busy: true, messages: [...state.currentTask.messages, userMessage] }
                : null,
        }));

        try {
            await taskService.sendMessageToTask(content, currentTask.id);
        } catch (error: unknown) {
            set({ error: error instanceof Error ? error.message : String(error) });
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

        set((state) => ({
            pendingToolApproval: null,
            currentTask: state.currentTask ? { ...state.currentTask, is_busy: approved } : null,
        }));
        try {
            await taskService.approveToolCall(currentTask.id, toolCallId, approved);
        } catch (error: unknown) {
            set({ error: error instanceof Error ? error.message : String(error) });
        }
    },

    interruptTask: async (taskId: string) => {
        try {
            await taskService.interruptTask(taskId);
        } catch (error: unknown) {
            console.error('Failed to interrupt task:', error);
        }
    },
}));

const handleTaskEvent = (event: TaskEvent, set: StoreApi<TaskState>['setState'], get: StoreApi<TaskState>['getState']) => {
    const { currentTask, currentAgentMessageId } = get();
    if (!currentTask) return;
    console.log('handleTaskEvent', event);
    switch (event.type) {
        case 'assistant_chunk': {
            const blocks = (event.parsed_content || []).map(block => ({
                ...block,
                status: block.type === 'tool_use' ? 'pending' : undefined
            })) as any[];

            if (currentAgentMessageId) {
                set((state: TaskState) => ({
                    currentTask: state.currentTask ? {
                        ...state.currentTask,
                        messages: state.currentTask.messages.map(msg =>
                            msg.id === currentAgentMessageId
                                ? { ...msg, blocks }
                                : msg
                        )
                    } : null
                }));
            } else {
                const newMessage: Message = {
                    id: uuidv4(),
                    sender: 'agent',
                    timestamp: new Date().toISOString(),
                    blocks
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
        }

        case 'assistant_complete':
            set((state) => ({
                currentAgentMessageId: null,
                currentTask: state.currentTask ? { ...state.currentTask, is_busy: false } : null,
            }));
            break;

        case 'tool_approval_request':
            // Clear currentAgentMessageId so the next chunk starts a new message block
            // Also unset is_busy since we are waiting on the user
            if (event.tool_call) {
                set((state) => ({
                    currentAgentMessageId: null,
                    currentTask: state.currentTask ? { ...state.currentTask, is_busy: false } : null,
                    pendingToolApproval: {
                        toolCallId: event.tool_call!.id,
                        toolName: event.tool_call!.name,
                        input: event.tool_call!.input,
                    }
                }));
            } else if (event.parsed_content) {
                const toolBlock = event.parsed_content.find(b => b.type === 'tool_use');
                if (toolBlock) {
                    set((state) => ({
                        currentAgentMessageId: null,
                        currentTask: state.currentTask ? { ...state.currentTask, is_busy: false } : null,
                        pendingToolApproval: {
                            toolCallId: toolBlock.id || 'pending', // Fallback if backend doesn't provide ID
                            toolName: toolBlock.name || '',
                            input: toolBlock.params || {},
                        }
                    }));
                }
            }
            break;

        case 'tool_executed':
            set((state: TaskState) => {
                if (!state.currentTask) return state;

                const updatedMessages = state.currentTask.messages.map(msg => {
                    if (msg.sender === 'agent') {
                        return {
                            ...msg,
                            blocks: msg.blocks.map(block =>
                                block.type === 'tool_use' && block.name === event.tool_name && block.status === 'pending'
                                    ? { ...block, status: 'executed' as const, result: event.result }
                                    : block
                            )
                        };
                    }
                    return msg;
                });

                return {
                    currentAgentMessageId: null,
                    currentTask: {
                        ...state.currentTask,
                        messages: updatedMessages
                    }
                };
            });
            break;

        case 'task_status':
            if (event.is_busy !== undefined) {
                set((state: TaskState) => ({
                    currentTask: state.currentTask ? { ...state.currentTask, is_busy: event.is_busy } : null
                }));
            }
            break;

        case 'error':
            set((state) => ({
                error: event.error || 'Unknown error',
                currentTask: state.currentTask ? { ...state.currentTask, is_busy: false } : null,
            }));
            break;
    }
};
