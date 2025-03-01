import unittest
import requests

BASE_URL = "http://localhost:5000"

class TestTodoAPI(unittest.TestCase):
    def test_1_create_task(self):
        new_task = {"title": "New Task", "description": "This is a new task"}
        response = requests.post(f"{BASE_URL}/tasks", json=new_task)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "New Task")

    def test_2_get_all_tasks(self):
        response = requests.get(f"{BASE_URL}/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_3_get_task_by_id(self):
        response = requests.get(f"{BASE_URL}/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)

    def test_4_update_task(self):
        updated_task = {"title": "Updated Task", "description": "This task has been updated"}
        response = requests.put(f"{BASE_URL}/tasks/1", json=updated_task)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Task")

    def test_5_delete_task(self):
        response = requests.delete(f"{BASE_URL}/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], True)

if __name__ == "__main__":
    unittest.main()