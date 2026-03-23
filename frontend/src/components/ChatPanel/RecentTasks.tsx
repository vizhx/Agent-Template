import React, { useEffect, useState } from 'react';
import { useTaskStore } from '../../store/taskStore';
import type { Task } from '../../types';

const RecentTasks: React.FC = () => {
    const [recentTasks, setRecentTasks] = useState<Task[]>([]);
    const { loadTasks, loadTask } = useTaskStore();

    useEffect(() => {
        const fetchRecentTasks = async () => {
            const tasks = await loadTasks();
            setRecentTasks(tasks);
        };
        fetchRecentTasks();
    }, [loadTasks]);

    const handleTaskClick = (taskId: string) => {
        loadTask(taskId);
    };

    if (recentTasks.length === 0) {
        return (
            <div className="flex items-center justify-center h-full text-muted-foreground p-4">
                <p className="text-sm">No recent tasks. Create a new task to get started.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-2 p-4">
            <h3 className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-2">Recent Tasks</h3>
            {recentTasks.map((task) => (
                <button
                    key={task.id}
                    onClick={() => handleTaskClick(task.id)}
                    className="text-left p-3 rounded-lg border border-border bg-card hover:bg-accent hover:border-accent-foreground transition-colors"
                >
                    <div className="font-medium text-sm text-foreground">{task.title}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                        {new Date(task.created_at).toLocaleDateString()}
                    </div>
                </button>
            ))}
        </div>
    );
};

export default RecentTasks;
