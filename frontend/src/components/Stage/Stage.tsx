import React, { useEffect } from 'react';
import { useContentStore } from '../../store/contentStore';
import ReactDiffViewerFactory from 'react-diff-viewer-continued';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Correctly import the default component, handling differences in CJS vs import
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ReactDiffViewer = (ReactDiffViewerFactory as any).default || ReactDiffViewerFactory;

const Stage: React.FC = () => {
    const { currentContent, isPreviewOpen, oldHtmlContent, newHtmlContent, subscribe, unsubscribe } = useContentStore();

    useEffect(() => {
        subscribe();
        return () => {
            unsubscribe();
        };
    }, [subscribe, unsubscribe]);

    if (isPreviewOpen) {
        return (
            <div className="flex flex-col h-full bg-background border-r border-border">
                <div className="p-4 border-b border-border bg-muted/30">
                    <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">Stage - Diff View</h2>
                </div>
                <div className="flex-1 overflow-auto p-4 bg-white dark:bg-gray-900">
                    <ReactDiffViewer
                        oldValue={oldHtmlContent}
                        newValue={newHtmlContent}
                        splitView={true}
                        useDarkTheme={document.documentElement.classList.contains('dark')}
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-background border-r border-border">
            <div className="p-4 ">
                <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">Stage</h2>
            </div>
            <div className="flex-1 overflow-auto p-4">
                {currentContent ? (
                    <div className="prose dark:prose-invert max-w-none bg-card p-6 rounded-lg shadow-sm border border-border">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {currentContent}
                        </ReactMarkdown>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                        No content to display
                    </div>
                )}
            </div>
        </div>
    );
};

export default Stage;
