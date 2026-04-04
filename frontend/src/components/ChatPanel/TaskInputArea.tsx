import React, { useState, useRef, useEffect } from 'react';
import { useTaskStore } from '../../store/taskStore';
import { Send, Loader2, Square } from 'lucide-react';

interface TaskInputAreaProps {
    isLoading: boolean;
}

const TaskInputArea: React.FC<TaskInputAreaProps> = ({ isLoading }) => {
    const [message, setMessage] = useState('');
    const { currentTask, sendMessage, interruptTask } = useTaskStore();
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const isBusy = currentTask?.is_busy || false;

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!message.trim() || isLoading || isBusy) return;

        const content = message;
        setMessage('');
        await sendMessage(content);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [message]);

    return (
        <div className="p-4 bg-background">
            <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={isBusy ? "Agent is responding..." : "Type a message..."}
                    disabled={isLoading || isBusy}
                    className="flex-1 min-h-[44px] max-h-[200px] p-3 pr-12 rounded-lg border border-input bg-background resize-none focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
                    rows={1}
                />
                {isBusy ? (
                    <button
                        type="button"
                        onClick={() => currentTask && interruptTask(currentTask.id)}
                        disabled={isLoading}
                        className="absolute right-2 bottom-2 p-2 rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors flex items-center justify-center disabled:opacity-50"
                        title="Stop Generation"
                    >
                        <Square size={16} className="fill-current" />
                    </button>
                ) : (
                    <button
                        type="submit"
                        disabled={!message.trim() || isLoading}
                        className="absolute right-2 bottom-2 p-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                    </button>
                )}
            </form>

        </div>
    );
};

export default TaskInputArea;
