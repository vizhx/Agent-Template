import { create } from 'zustand';
import { subscribeToContentUpdates } from '../services/contentService';
import type { ContentEvent } from '../types';

interface ContentState {
    currentContent: string;
    isPreviewOpen: boolean;
    oldHtmlContent: string;
    newHtmlContent: string;
    cleanup: (() => void) | null;

    closePreview: () => void;
    subscribe: () => void;
    unsubscribe: () => void;
}

export const useContentStore = create<ContentState>((set, get) => ({
    currentContent: '',
    isPreviewOpen: false,
    oldHtmlContent: '',
    newHtmlContent: '',
    cleanup: null,

    closePreview: () => {
        set({ isPreviewOpen: false, oldHtmlContent: '', newHtmlContent: '' });
    },

    subscribe: () => {
        console.log("Subsrcibing to content updates")
        const { unsubscribe } = get();
        unsubscribe();

        const eventSource = subscribeToContentUpdates((event) => {
            const data: ContentEvent = JSON.parse(event.data);
            console.log("Received content event:", data);
            if (data.type === 'initial_content') {
                set({ currentContent: data.content || '' });
            } else if (data.type === 'content_preview') {
                set({
                    isPreviewOpen: true,
                    oldHtmlContent: data.old_content || '',
                    newHtmlContent: data.new_content || ''
                });
            } else if (data.type === 'content_updated') {
                set({
                    currentContent: data.content || '',
                    isPreviewOpen: false
                });
            }
        });

        set({ cleanup: () => eventSource.close() });
    },

    unsubscribe: () => {
        const { cleanup } = get();
        if (cleanup) {
            cleanup();
            set({ cleanup: null });
        }
    },
}));
