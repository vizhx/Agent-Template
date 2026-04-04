from rest_framework.test import APITestCase
from rest_framework import status

class TaskViewSetTests(APITestCase):
    def test_create_task(self):
        url = "/api/tasks/"
        data = {'title': 'Test Task', 'userId': 'user-1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], 'Test Task')

    def test_list_tasks(self):
        url = "/api/tasks/"
        data = {'title': 'Test 1', 'userId': 'user-1'}
        self.client.post(url, data, format='json')
        
        response = self.client.get("/api/tasks/?user_id=user-1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
