import json
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://127.0.0.1:8000/"
RESULT_PATH = Path(__file__).resolve().parent / "result_test_selenium.json"


def tc(test_id: str):
    """
    Décorateur pour taguer un test Selenium avec un ID de cahier de tests (TC016, etc.).
    Il ajoute un attribut .test_case_id à la méthode de test.
    """

    def decorator(func):
        func.test_case_id = test_id
        return func

    return decorator


class JsonSeleniumResult(unittest.TextTestResult):
    """
    Résultat de tests Selenium qui garde les infos dans une liste
    et peut les écrire dans result_test_selenium.json.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_results = []

    def _record(self, test, status):
        test_case_id = getattr(test, "test_case_id", None)

        if test_case_id is None:
            method_name = getattr(test, "_testMethodName", None)
            if method_name and hasattr(test, method_name):
                method = getattr(test, method_name)
                test_case_id = getattr(method, "test_case_id", None)

        self.json_results.append(
            {
                "test_case_id": test_case_id,
                "test_name": self.getDescription(test),
                "status": status,
            }
        )

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "error")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "skipped")

    def write_json(self, path: Path):
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.json_results, f, indent=2, ensure_ascii=False)


class TodoListE2ETest(unittest.TestCase):
    def setUp(self):
        print("✅ setUp: lancement du navigateur")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 5)

    def tearDown(self):
        print("✅ tearDown: fermeture du navigateur")
        self.driver.quit()

    def _go_home(self):
        print(f"▶️  Navigation vers {BASE_URL}")
        self.driver.get(BASE_URL)
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".todo-list"))
        )

    def _count_tasks(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".item-row")
        return len(rows)

    def _create_task(self, title: str):
        input_title = self.wait.until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        input_title.clear()
        input_title.send_keys(title)
        input_title.send_keys(Keys.RETURN)
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item-row"))
        )

    def _delete_last_task(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".item-row")
        if not rows:
            return
        last_row = rows[-1]
        delete_link = last_row.find_element(By.LINK_TEXT, "Delete")
        delete_link.click()

        confirm_button = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            )
        )
        confirm_button.click()

        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".todo-list"))
        )

    @tc("TC016")
    def test_create_and_delete_10_tasks_keeps_task_count(self):
        """
        TC016 auto (Selenium) :
        - Se connecter à l'app
        - Compter les tâches
        - Créer 10 tâches
        - Supprimer ces 10 tâches
        - Vérifier que le nombre final = nombre initial
        """
        print("🚀 Début du test E2E Selenium")
        self._go_home()

        initial_count = self._count_tasks()
        print(f"Nombre initial de tâches : {initial_count}")

        for i in range(10):
            self._create_task(f"E2E selenium task {i+1}")
            time.sleep(0.2)

        after_creation_count = self._count_tasks()
        print(f"Nombre après création : {after_creation_count}")

        for _ in range(10):
            self._delete_last_task()
            time.sleep(0.2)

        final_count = self._count_tasks()
        print(f"Nombre final de tâches : {final_count}")

        self.assertEqual(
            initial_count,
            final_count,
            "Le nombre final de tâches devrait être égal au nombre initial.",
        )
        print("✅ Test E2E terminé avec succès")

    @tc("TC017")
    def test_first_task_stays_when_deleting_second(self):
        """
        TC017 auto (Selenium) :
        - Aller sur la home
        - Créer une tâche A (titre unique), mémoriser son nom
        - Créer une tâche B
        - Supprimer la dernière tâche (B)
        - Vérifier que A est toujours présente dans la liste
        """
        print("🚀 Début du test E2E Selenium TC017")
        self._go_home()

        # Créer une tâche A avec un titre unique
        task_a_title = "E2E impact A"
        self._create_task(task_a_title)
        time.sleep(0.2)

        # Créer une tâche B
        task_b_title = "E2E impact B"
        self._create_task(task_b_title)
        time.sleep(0.2)

        # Supprimer la dernière tâche créée (normalement B)
        self._delete_last_task()
        time.sleep(0.2)

        # Vérifier que la tâche A est toujours présente dans la page
        elements_with_a = self.driver.find_elements(
            By.XPATH, f"//*[text()='{task_a_title}']"
        )
        self.assertTrue(
            elements_with_a,
            "La tâche A devrait toujours être présente après suppression de B.",
        )
        print("✅ TC017 terminé avec succès : A est toujours présente")



if __name__ == "__main__":
    print("▶️ Lancement des tests Selenium (unittest avec JSON)...")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TodoListE2ETest)
    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=JsonSeleniumResult,
    )
    result: JsonSeleniumResult = runner.run(suite)

    # écriture du JSON
    result.write_json(RESULT_PATH)
    print(f"\n📄 Résultats Selenium JSON écrits dans : {RESULT_PATH}")

    # code de retour : 0 si tout passe, 1 sinon
    import sys

    sys.exit(not result.wasSuccessful())
