import json
import os
import sys
import unittest
from pathlib import Path

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
django.setup()


class JsonTestResult(unittest.TextTestResult):
    """
    TestResult personnalisé qui enregistre le résultat des tests
    et peut les exporter en JSON (result_test_auto.json).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_results = []

    def _record(self, test, status):
        # On récupère d'abord l'ID éventuel sur l'instance de test
        test_case_id = getattr(test, "test_case_id", None)

        # Si rien sur l'instance, on va chercher sur la méthode de test
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


class JsonDiscoverRunner(DiscoverRunner):
    """
    Test runner Django custom qui utilise JsonTestResult
    et génère le fichier result_test_auto.json.
    """

    def run_suite(self, suite, **kwargs):
        test_runner = unittest.TextTestRunner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            buffer=self.buffer,
            resultclass=JsonTestResult,
        )
        result: JsonTestResult = test_runner.run(suite)

        # Fichier JSON de sortie à la racine du projet
        output_path = Path(settings.BASE_DIR) / "result_test_auto.json"
        result.write_json(output_path)
        print(f"\n📄 Résultats JSON écrits dans {output_path}")

        return result


if __name__ == "__main__":
    # On ne lance que les tests de l'app tasks
    test_labels = ["tasks"]

    runner = JsonDiscoverRunner(verbosity=1)
    failures = runner.run_tests(test_labels)

    sys.exit(bool(failures))
