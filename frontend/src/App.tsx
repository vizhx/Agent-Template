import { useEffect } from 'react';
import { useTaskStore } from './store/taskStore';
import ChatPanel from './components/ChatPanel/ChatPanel';
import Stage from './components/Stage/Stage';
import { Loader2 } from 'lucide-react';

function App() {
  const {
    currentTask,
    isLoading,
    createTask,
    syncWithBackend,
    approveToolCall,
    pendingToolApproval
  } = useTaskStore();

  useEffect(() => {
    // Initial setup: try to sync or create a default task
    const init = async () => {
      await syncWithBackend();
      const state = useTaskStore.getState();
      if (!state.currentTask) {
        await createTask("New Session");
      }
    };
    init();
  }, [syncWithBackend, createTask]);

  if (!currentTask && isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-foreground">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      {/* Stage Area (Left/Main) */}
      <div className="flex-1 h-full overflow-hidden">
        <Stage />
      </div>

      {/* Chat Area (Right Sidebar) */}
      <ChatPanel
        currentTask={currentTask}
        isLoading={isLoading}
        onToolApproval={approveToolCall}
        pendingToolApproval={pendingToolApproval}
      />
    </div>
  );
}

export default App;
