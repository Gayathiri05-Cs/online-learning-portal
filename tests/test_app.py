import os
import tempfile
import unittest
import app as portal

class PortalApiTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        portal.DB_PATH = os.path.join(self.tempdir.name, "test.db")
        portal.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        portal.init_db()
        self.client = portal.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def register(self, email="student@example.com", password="securepass123"):
        return self.client.post("/api/auth/register", json={
            "name": "Test Student", "email": email, "password": password
        })

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"LearnSpace", response.data)

    def test_sample_courses_exist(self):
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 6)

    def test_register_valid_user(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)

    def test_duplicate_email_rejected(self):
        self.register()
        response = self.register()
        self.assertEqual(response.status_code, 409)

    def test_weak_password_rejected(self):
        response = self.register(password="123")
        self.assertEqual(response.status_code, 400)

    def test_login_and_enrollment(self):
        self.register()
        response = self.client.post("/api/courses/1/enroll", json={})
        self.assertEqual(response.status_code, 201)
        courses = self.client.get("/api/my-courses").get_json()
        self.assertEqual(len(courses), 1)

    def test_course_search(self):
        response = self.client.get("/api/courses?search=Python")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_lesson_completion_updates_progress(self):
        self.register()
        self.client.post("/api/courses/1/enroll", json={})
        lesson_id = portal.get_db().execute(
            "SELECT id FROM lessons WHERE course_id=1 ORDER BY lesson_order LIMIT 1"
        ).fetchone()["id"]
        response = self.client.post(f"/api/lessons/{lesson_id}/complete", json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["progress"], 25)

    def test_lesson_completion_requires_enrollment(self):
        response = self.client.post("/api/lessons/1/complete", json={})
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
