import React, { useEffect, useRef } from 'react';
import type { Message } from '../../types';
import MessageGroup from './MessageGroup';

interface TaskMessageListProps {
    messages: Message[];
    onToolApproval?: (toolCallId: string, approved: boolean) => void;
    pendingToolApproval?: {
        toolCallId: string;
        toolName: string;
        input: Record<string, unknown>;
    } | null;
}

const TaskMessageList: React.FC<TaskMessageListProps> = ({ messages, onToolApproval, pendingToolApproval }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, pendingToolApproval]);

    // Group messages
    const groupedMessages: { sender: 'user' | 'agent'; messages: Message[] }[] = [];

    messages.forEach((message) => {
        const lastGroup = groupedMessages[groupedMessages.length - 1];
        if (lastGroup && lastGroup.sender === message.sender) {
            lastGroup.messages.push(message);
        } else {
            groupedMessages.push({ sender: message.sender, messages: [message] });
        }
    });

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {groupedMessages.map((group, index) => (
                <MessageGroup
                    key={index}
                    messages={group.messages}
                    sender={group.sender}
                    onToolApproval={index === groupedMessages.length - 1 ? onToolApproval : undefined}
                    pendingToolApproval={index === groupedMessages.length - 1 ? pendingToolApproval : undefined}
                />
            ))}
            <div ref={bottomRef} />
        </div>
    );
};

export default TaskMessageList;
