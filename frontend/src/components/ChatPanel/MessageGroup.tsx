import React from 'react';
import type { Message } from '../../types';
import TaskMessageItem from './TaskMessageItem';

interface MessageGroupProps {
    messages: Message[];
    sender: 'user' | 'agent';
    onToolApproval?: (toolCallId: string, approved: boolean) => void;
    pendingToolApproval?: {
        toolCallId: string;
        toolName: string;
        input: Record<string, unknown>;
    } | null;
}

const MessageGroup: React.FC<MessageGroupProps> = ({ messages, sender, onToolApproval, pendingToolApproval }) => {
    const isUser = sender === 'user';

    return (
        <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}`}>
                    {isUser ? '👤' : '🤖'}
                </div>
                <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{isUser ? 'You' : 'Agent'}</span>
                        <span>{new Date(messages[0].timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className={`p-3 rounded-lg ${isUser ? 'bg-primary text-primary-foreground' : 'bg-card border border-border'} overflow-hidden max-w-full flex flex-col gap-4 shadow-sm`}>
                        {messages.map((message, index) => (
                            <TaskMessageItem
                                key={message.id}
                                message={message}
                                onToolApproval={index === messages.length - 1 ? onToolApproval : undefined}
                                pendingToolApproval={index === messages.length - 1 ? pendingToolApproval : undefined}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MessageGroup;
