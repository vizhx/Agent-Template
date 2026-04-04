from django.test import SimpleTestCase
import asyncio
from chat.tools.all_tools import EditContentTool, GetCurrentContentTool, CompleteTaskTool
from chat.content_manager import content_manager

class ToolTests(SimpleTestCase):
    def setUp(self):
        # Reset content for each test
        content_manager.current_content = ""
        super().setUp()

    def test_get_current_content_tool(self):
        tool = GetCurrentContentTool()
        content_manager.current_content = "Test Content"
        
        async def run_test():
            result = await tool.execute({}, "task-1")
            self.assertEqual(result, "Test Content")
            
        asyncio.run(run_test())

    def test_edit_content_tool(self):
        tool = EditContentTool()
        
        async def run_test():
            result = await tool.execute({"newContent": "Edited Content"}, "task-1")
            self.assertEqual(result, "Content updated successfully.")
            self.assertEqual(content_manager.get_content(), "Edited Content")
            
        asyncio.run(run_test())

    def test_complete_task_tool(self):
        tool = CompleteTaskTool()
        async def run_test():
            result = await tool.execute({"summary": "All done!"}, "task-1")
            self.assertEqual(result, "Task marked as complete: All done!")
        asyncio.run(run_test())
