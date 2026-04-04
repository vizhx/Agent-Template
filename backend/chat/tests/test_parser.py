from django.test import SimpleTestCase
from chat.message_parser import parse_assistant_message

class MessageParserTests(SimpleTestCase):
    def test_parse_text_and_tool(self):
        message = (
            "Here is the content.\n"
            "<edit_content>\n"
            "<newContent>Hello World</newContent>\n"
            "</edit_content>\n"
            "Done."
        )
        blocks = parse_assistant_message(message)
        
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0]["type"], "text")
        self.assertEqual(blocks[0]["content"], "Here is the content.")
        
        self.assertEqual(blocks[1]["type"], "tool_use")
        self.assertEqual(blocks[1]["name"], "edit_content")
        self.assertEqual(blocks[1]["params"]["newContent"], "Hello World")
        self.assertFalse(blocks[1]["partial"])
        
        self.assertEqual(blocks[2]["type"], "text")
        self.assertEqual(blocks[2]["content"], "Done.")
        
    def test_parse_partial_tool(self):
        message = "<get_current_content>"
        blocks = parse_assistant_message(message)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["type"], "tool_use")
        self.assertEqual(blocks[0]["name"], "get_current_content")
        self.assertTrue(blocks[0]["partial"])
