from pathlib import Path
import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task
from tasks.utils import import_tasks_from_dataset


def tc(test_id: str):
    """
    Décorateur pour taguer un test Django avec un ID de cahier de tests (TC001, etc.).
    Il ajoute un attribut .test_case_id à la méthode de test.
    """

    def decorator(func):
        func.test_case_id = test_id
        return func

    return decorator


class TaskViewsTests(TestCase):
    def setUp(self):
        # Crée une tâche de test pour les vues qui ont besoin d'un ID
        self.task = Task.objects.create(title="Test task", complete=False)

    @tc("TC001")
    def test_index_url_status_code(self):
        """
        La page d'accueil '/' doit répondre avec un code HTTP 200.
        """
        response = self.client.get(reverse("list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test task")

    @tc("TC002")
    def test_update_task_url_status_code_get(self):
        """
        La page '/update_task/ID/' doit répondre 200 en GET.
        """
        url = reverse("update_task", kwargs={"pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # On doit voir le titre de la tâche dans le formulaire
        self.assertContains(response, "Test task")

    @tc("TC006")
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

    @tc("TC003")
    def test_delete_task_url_status_code_get(self):
        """
        La page '/delete_task/ID/' doit répondre 200 en GET (page de confirmation).
        """
        url = reverse("delete", kwargs={"pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test task")

    @tc("TC007")
    def test_delete_task_url_status_code_post(self):
        """
        En POST sur '/delete_task/ID/', la tâche doit être supprimée puis redirection.
        """
        url = reverse("delete", kwargs={"pk": self.task.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    @tc("TC008")
    def test_task_str_returns_title(self):
        task = Task.objects.create(title="My title", complete=False)
        self.assertEqual(str(task), "My title")

    @tc("TC010")
    def test_version_is_displayed_on_home(self):
        """
        La page d'accueil affiche la version de l'application.
        """
        response = self.client.get(reverse("list"))
        self.assertContains(response, str(settings.VERSION))


class DatasetImportTests(TestCase):
    def setUp(self):
        # On pointe vers dataset.json à la racine du projet
        self.dataset_path = Path(settings.BASE_DIR) / "dataset.json"

    def test_dataset_file_exists_and_is_valid_json(self):
        # Le fichier doit exister
        self.assertTrue(self.dataset_path.exists())

        # Le JSON doit être valide
        with self.dataset_path.open(encoding="utf-8") as f:
            data = json.load(f)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("title", data[0])

    @tc("TC009")
    def test_import_tasks_from_dataset_creates_tasks_in_db(self):
        # On s'assure que la base est vide au départ
        Task.objects.all().delete()
        self.assertEqual(Task.objects.count(), 0)

        created_count = import_tasks_from_dataset(self.dataset_path)

        # Le nombre retourné doit être > 0
        self.assertGreater(created_count, 0)

        # Et la base doit contenir autant de tâches
        self.assertEqual(Task.objects.count(), created_count)

        # On peut vérifier qu'une des tâches du dataset est bien présente
        self.assertTrue(
            Task.objects.filter(title="Acheter du pain").exists()
        )
