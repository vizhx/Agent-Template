export interface User {
    id: string;
    username: string;
    email?: string;
}

export interface Task {
    id: string;
    title: string;
    status: 'active' | 'completed' | 'archived';
    created_at: string;
    updated_at: string;
    messages: Message[];
}

export type MessageSender = 'user' | 'agent';

export interface Message {
    id: string;
    task_id: string;
    sender: MessageSender;
    content: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
    tool_calls?: ToolCall[];
}

export interface ToolCall {
    id: string;
    name: string;
    input: Record<string, unknown>;
    status: 'pending' | 'approved' | 'rejected' | 'executed' | 'failed';
    result?: string;
    error?: string;
}

export interface Content {
    id: string;
    task_id: string;
    html_content: string;
    version: number;
    created_at: string;
}

export interface TaskEvent {
    type: 'user_message' | 'assistant_chunk' | 'assistant_complete' | 'tool_approval_request' | 'tool_executed' | 'error';
    payload: any;
}

export interface ContentEvent {
    type: 'initial_content' | 'content_preview' | 'content_updated' | 'error';
    content?: string;
    old_content?: string;
    new_content?: string;
}
