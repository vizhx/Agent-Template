import React from 'react';
import type { Message } from '../../types';
import { Check, X, Wrench } from 'lucide-react';

interface TaskMessageItemProps {
    message: Message;
    onToolApproval?: (toolCallId: string, approved: boolean) => void;
    pendingToolApproval?: {
        toolCallId: string;
        toolName: string;
        input: Record<string, unknown>;
    } | null;
}

const TaskMessageItem: React.FC<TaskMessageItemProps> = ({ message, onToolApproval, pendingToolApproval }) => {
    const isUser = message.sender === 'user';

    return (
        <div className={`p-3 rounded-lg ${isUser ? 'bg-primary text-primary-foreground' : 'bg-card border border-border'}`}>
            <div className="whitespace-pre-wrap text-sm">{message.content}</div>

            {/* Tool Calls Display */}
            {message.tool_calls && message.tool_calls.length > 0 && (
                <div className="mt-2 flex flex-col gap-2">
                    {message.tool_calls.map((toolCall) => (
                        <div key={toolCall.id} className="bg-secondary/50 p-2 rounded text-xs">
                            <div className="flex items-center gap-1 font-semibold">
                                <Wrench size={12} />
                                {toolCall.name}
                            </div>
                            <pre className="mt-1 overflow-x-auto bg-background/50 p-1 rounded">
                                {JSON.stringify(toolCall.input, null, 2)}
                            </pre>
                            {toolCall.result && (
                                <div className="mt-1 text-muted-foreground border-t border-border/50 pt-1">
                                    Result: {toolCall.result.substring(0, 100)}...
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Pending Tool Approval */}
            {pendingToolApproval && onToolApproval && (
                <div className="mt-2 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded">
                    <div className="text-xs font-semibold text-yellow-600 dark:text-yellow-400 mb-1">
                        Approval Required: {pendingToolApproval.toolName}
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onToolApproval(pendingToolApproval.toolCallId, true)}
                            className="flex items-center gap-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                        >
                            <Check size={12} /> Approve
                        </button>
                        <button
                            onClick={() => onToolApproval(pendingToolApproval.toolCallId, false)}
                            className="flex items-center gap-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                        >
                            <X size={12} /> Reject
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TaskMessageItem;
