import React, { useEffect } from 'react';
import { useContentStore } from '../../store/contentStore';

const Stage: React.FC = () => {
    const { currentContent, isPreviewOpen, oldHtmlContent, newHtmlContent, subscribe, unsubscribe } = useContentStore();

    useEffect(() => {
        subscribe();
        console.log("Current content:", currentContent);
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
                <div className="flex-1 overflow-auto p-4 flex gap-4">
                    <div className="flex-1">
                        <div className="prose dark:prose-invert max-w-none border rounded-md p-4 bg-card" dangerouslySetInnerHTML={{ __html: oldHtmlContent }} />
                    </div>
                    <div className="flex-1">
                        <div className="prose dark:prose-invert max-w-none border rounded-md p-4 bg-card" dangerouslySetInnerHTML={{ __html: newHtmlContent }} />
                    </div>
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
                    <div className="prose dark:prose-invert max-w-none bg-card p-6 rounded-lg shadow-sm border border-border" dangerouslySetInnerHTML={{ __html: currentContent }} />
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
