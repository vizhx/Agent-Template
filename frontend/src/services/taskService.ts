import api from './api';
import type { Task } from '../types';

export const createTask = async (title: string): Promise<Task> => {
    const response = await api.post('/api/tasks/', { title, userId: 'user-1' }); // Hardcoded userId for now
    return response.data;
};

export const getTask = async (taskId: string): Promise<Task> => {
    const response = await api.get(`/api/tasks/${taskId}/`);
    return response.data;
};

export const getUserTasks = async (userId: string): Promise<Task[]> => {
    const response = await api.get(`/api/tasks/?user_id=${userId}`);
    return response.data;
};

export const sendMessageToTask = async (content: string, taskId: string): Promise<void> => {
    await api.post(`/api/tasks/${taskId}/messages/`, { content });
};

export const approveToolCall = async (taskId: string, toolCallId: string, approved: boolean): Promise<void> => {
    await api.post(`/api/tasks/${taskId}/approve-tool/`, { toolCallId, approved });
};

export const interruptTask = async (taskId: string): Promise<void> => {
    await api.post(`/api/tasks/${taskId}/interrupt/`);
};
