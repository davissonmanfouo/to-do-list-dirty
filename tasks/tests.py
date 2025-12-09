from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskViewsTests(TestCase):
    def setUp(self):
        # Crée une tâche de test pour les vues qui ont besoin d'un ID
        self.task = Task.objects.create(title="Test task", complete=False)

    def test_index_url_status_code(self):
        """
        La page d'accueil '/' doit répondre avec un code HTTP 200.
        """
        response = self.client.get(reverse("list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test task")

    def test_update_task_url_status_code_get(self):
        """
        La page '/update_task/ID/' doit répondre 200 en GET.
        """
        url = reverse("update_task", kwargs={"pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # On doit voir le titre de la tâche dans le formulaire
        self.assertContains(response, "Test task")

    def test_update_task_url_status_code_post(self):
        """
        En POST sur '/update_task/ID/', la tâche doit être mise à jour puis redirection.
        """
        url = reverse("update_task", kwargs={"pk": self.task.id})
        response = self.client.post(
            url,
            {"title": "Updated task", "complete": True},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated task")
        self.assertTrue(self.task.complete)

    def test_delete_task_url_status_code_get(self):
        """
        La page '/delete_task/ID/' doit répondre 200 en GET (page de confirmation).
        """
        url = reverse("delete_task", kwargs={"pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test task")

    def test_delete_task_url_status_code_post(self):
        """
        En POST sur '/delete_task/ID/', la tâche doit être supprimée puis redirection.
        """
        url = reverse("delete_task", kwargs={"pk": self.task.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
    def test_task_str_returns_title(self):
        task = Task.objects.create(title="My title", complete=False)
        self.assertEqual(str(task), "My title")
    


