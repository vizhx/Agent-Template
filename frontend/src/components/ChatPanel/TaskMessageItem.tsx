import React from 'react';
import type { Message } from '../../types';
import { Check, X, Wrench, Loader2 } from 'lucide-react';

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
    return (
        <div className="flex flex-col gap-2">
            {message.blocks?.map((block, idx) => {
                if (block.type === 'text') {
                    if (!block.content?.trim()) return null;
                    return (
                        <div key={idx} className="whitespace-pre-wrap break-words text-sm">
                            {block.content.trim()}
                        </div>
                    );
                }
                
                if (block.type === 'tool_use') {
                    return (
                        <div key={idx} className="bg-secondary/50 px-3 py-2 rounded text-xs flex flex-col gap-1 font-medium">
                            <div className="flex items-center gap-2">
                                <Wrench size={12} className="text-muted-foreground" />
                                <span className={block.status === 'pending' ? 'animate-pulse text-muted-foreground' : ''}>
                                    {block.name || 'Using tool...'}
                                </span>
                                {block.status === 'pending' && <Loader2 size={10} className="animate-spin text-muted-foreground" />}
                            </div>
                            {(block.status === 'pending' || !block.status) && block.params && Object.keys(block.params).length > 0 && (
                                <div className="text-[10px] text-muted-foreground font-mono mt-1 w-full truncate opacity-70">
                                    {JSON.stringify(block.params)}
                                </div>
                            )}
                            {block.status === 'executed' && block.result && (
                                <div className="text-[10px] text-muted-foreground mt-1 border-t border-border/50 pt-1">
                                    Result: {block.result.length > 200 ? block.result.substring(0, 200) + '...' : block.result}
                                </div>
                            )}
                        </div>
                    );
                }
                return null;
            })}

            {/* Pending Tool Approval (Always at bottom) */}
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
