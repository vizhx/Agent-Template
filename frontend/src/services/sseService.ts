import { baseURL } from './api';

export const connectToTaskUpdates = (taskId: string, onMessage: (event: MessageEvent) => void): EventSource => {
    const url = `${baseURL}/api/tasks/${taskId}/stream/`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = onMessage;

    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
    };

    return eventSource;
};
