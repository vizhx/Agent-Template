import React, { useState } from 'react';
import TaskMessageList from './TaskMessageList';
import TaskInputArea from './TaskInputArea';
import RecentTasks from './RecentTasks';
import { useTaskStore } from '../../store/taskStore';
import type { Message } from '../../types';

interface ChatPanelProps {
    currentTask: { id: string; messages: Message[] } | null;
    isLoading: boolean;
    onToolApproval: (toolCallId: string, approved: boolean) => Promise<void>;
    pendingToolApproval: {
        toolCallId: string;
        toolName: string;
        input: Record<string, unknown>;
    } | null;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ currentTask, isLoading, onToolApproval, pendingToolApproval }) => {
    const [showNewTaskDialog, setShowNewTaskDialog] = useState(false);
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const { createTask, deleteTask } = useTaskStore();

    const handleCreateNewTask = async () => {
        if (newTaskTitle.trim()) {
            await createTask(newTaskTitle);
            setNewTaskTitle('');
            setShowNewTaskDialog(false);
        }
    };

    const handleAbandonTask = () => {
        if (currentTask && confirm('Are you sure you want to abandon this task?')) {
            deleteTask(currentTask.id);
        }
    };

    return (
        <div className="w-[400px] flex flex-col border-l border-border bg-card shadow-xl h-full">
            <div className="p-4 flex items-center justify-between border-b border-border">
                <h2 className="font-semibold text-sm uppercase tracking-wider text-foreground">Chat</h2>
                <div className="flex gap-2">
                    {currentTask && (
                        <button
                            onClick={handleAbandonTask}
                            className="p-1.5 rounded-md hover:bg-destructive/10 text-destructive transition-colors"
                            title="Abandon current task"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    )}
                    <button
                        onClick={() => setShowNewTaskDialog(true)}
                        className="p-1.5 rounded-md hover:bg-accent text-foreground transition-colors"
                        title="Create new task"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                </div>
            </div>

            {showNewTaskDialog && (
                <div className="p-4 border-b border-border bg-muted/30">
                    <input
                        type="text"
                        value={newTaskTitle}
                        onChange={(e) => setNewTaskTitle(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') handleCreateNewTask();
                            if (e.key === 'Escape') setShowNewTaskDialog(false);
                        }}
                        placeholder="Enter task title..."
                        className="w-full px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                        autoFocus
                    />
                    <div className="flex gap-2 mt-2">
                        <button
                            onClick={handleCreateNewTask}
                            className="px-3 py-1.5 text-xs rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                        >
                            Create
                        </button>
                        <button
                            onClick={() => setShowNewTaskDialog(false)}
                            className="px-3 py-1.5 text-xs rounded-md border border-border hover:bg-accent transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            <div className="flex-1 overflow-hidden relative flex flex-col">
                {currentTask ? (
                    <TaskMessageList
                        messages={currentTask.messages}
                        onToolApproval={onToolApproval}
                        pendingToolApproval={pendingToolApproval}
                    />
                ) : (
                    <RecentTasks />
                )}
            </div>
            {currentTask && <TaskInputArea isLoading={isLoading} />}
        </div>
    );
};

export default ChatPanel;
