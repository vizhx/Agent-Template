import { baseURL } from './api';

export const subscribeToContentUpdates = (onMessage: (event: MessageEvent) => void): EventSource => {
    const url = `${baseURL}/api/content-stream/`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = onMessage;

    eventSource.onerror = (error) => {
        console.error('Content SSE Error:', error);
        eventSource.close();
    };

    return eventSource;
};
