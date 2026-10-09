import unittest
from unittest.mock import patch, MagicMock
from app import app


class TaskFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.get_db_connection")
    def test_home(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "title": "Tâche Initiale",
                "description": "Desc",
                "category": "DevOps",
                "priority": "Haute",
                "status": "En cours",
                "created_at": "2026-10-09 18:00"
            }
        ]
        mock_get_db.return_value = mock_conn

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("TaskFlow", response.text)
        self.assertIn("Tâche Initiale", response.text)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["service"], "taskflow")

    @patch("app.get_db_connection")
    def test_ready_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "READY")

    @patch("app.get_db_connection")
    def test_ready_failure(self, mock_get_db):
        mock_get_db.side_effect = Exception("Connexion refusée")
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["status"], "NOT_READY")

    def test_add_task_validation(self):
        response = self.client.post("/add", data={"title": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Titre obligatoire", response.text)

    @patch("app.get_db_connection")
    def test_add_task_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = self.client.post("/add", data={"title": "Nouvelle Tâche", "category": "DevOps", "priority": "Haute"})
        self.assertEqual(response.status_code, 302)

    @patch("app.get_db_connection")
    def test_tasks_api(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "title": "Tâche Test",
                "description": "Description Test",
                "category": "DevOps",
                "priority": "Haute",
                "status": "A faire",
                "created_at": "2026-10-09 18:00:00"
            }
        ]
        mock_get_db.return_value = mock_conn

        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Tâche Test")
        self.assertFalse(data[0]["completed"])

    @patch("app.get_db_connection")
    def test_delete_task(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = self.client.delete("/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("supprimée", response.get_json()["message"])


if __name__ == "__main__":
    unittest.main()