import json
from pathlib import Path

import yaml  # nécessite pyyaml


BASE_DIR = Path(__file__).resolve().parent
TEST_LIST_PATH = BASE_DIR / "test_list.yaml"
RESULT_AUTO_PATH = BASE_DIR / "result_test_auto.json"


def load_test_list():
    with TEST_LIST_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("tests", [])


def load_auto_results():
    if not RESULT_AUTO_PATH.exists():
        return []
    with RESULT_AUTO_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def compute_status_for_test(test_case, auto_results):
    """
    Détermine le statut global du cas de test (PASS/FAIL/NOT_IMPLEMENTED/MANUAL_ONLY)
    en fonction :
    - du type (auto / manuel)
    - des résultats JSON (pour les auto uniquement)
    """

    tc_id = test_case["id"]
    tc_type = test_case["type"]

    # Tests manuels : on ne sait pas s'ils sont passés ou non → MANUAL_ONLY
    if tc_type in ("manuel", "manual"):
        return "MANUAL_ONLY"

    # Tests auto : on regarde dans result_test_auto.json
    matching_results = [
        r for r in auto_results if r.get("test_case_id") == tc_id
    ]

    if not matching_results:
        return "NOT_IMPLEMENTED"

    # S'il y a au moins un failed/error -> FAIL
    if any(r["status"] in {"failed", "error"} for r in matching_results):
        return "FAIL"

    # S'il y a au moins un skipped et aucun failed/error -> SKIPPED
    if any(r["status"] == "skipped" for r in matching_results):
        return "SKIPPED"

    # Si tous sont passed -> PASS
    if all(r["status"] == "passed" for r in matching_results):
        return "PASS"

    # Cas par défaut de sécurité
    return "UNKNOWN"


def percentage(part, total):
    if total == 0:
        return 0.0
    return round(part * 100.0 / total, 1)


def main():
    test_list = load_test_list()
    auto_results = load_auto_results()

    total = len(test_list)

    report_rows = []
    status_counts = {
        "PASS": 0,
        "FAIL": 0,
        "NOT_IMPLEMENTED": 0,
        "MANUAL_ONLY": 0,
        "SKIPPED": 0,
        "UNKNOWN": 0,
    }

    for tc in test_list:
        status = compute_status_for_test(tc, auto_results)
        row = {
            "id": tc["id"],
            "type": tc["type"],
            "description": tc.get("description", ""),
            "status": status,
        }
        report_rows.append(row)
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts["UNKNOWN"] += 1

    # --- Affichage détaillé par test ---
    print("\n===== TEST REPORT (J2 Exercice 5+6) =====\n")

    for row in report_rows:
        status = row["status"]
        if status == "PASS":
            icon = "✅"
        elif status == "FAIL":
            icon = "❌"
        elif status == "NOT_IMPLEMENTED":
            icon = "⚪"
        elif status == "MANUAL_ONLY":
            icon = "🫱"
        elif status == "SKIPPED":
            icon = "⏭️"
        else:
            icon = "❓"

        print(f"- {row['id']} [{row['type']}] | {icon} {status}")
        if row["description"]:
            print(f"    {row['description']}")

    # --- Résumé avec pourcentages ---
    passed = status_counts["PASS"]
    failed = status_counts["FAIL"]
    not_found = status_counts["NOT_IMPLEMENTED"]
    manual = status_counts["MANUAL_ONLY"]

    passed_plus_manual = passed + manual

    print("\n----- RÉSUMÉ -----")
    print(f"Number of tests: {total}")
    print(
        f"✅Passed tests: {passed} ({percentage(passed, total)}%)"
    )
    print(
        f"❌Failed tests: {failed} "
        f"({percentage(failed, total)}%)"
    )
    print(
        f"⚪Not found tests: {not_found} "
        f"({percentage(not_found, total)}%)"
    )
    print(
        f"🫱Test to pass manually: {manual} "
        f"({percentage(manual, total)}%)"
    )
    print(
        f"✅Passed + 🫱Manual: {passed_plus_manual} "
        f"({percentage(passed_plus_manual, total)}%)"
    )

    # Export JSON détaillé (optionnel mais pratique)
    output_path = BASE_DIR / "test_report.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report_rows, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Rapport détaillé écrit dans : {output_path}")


if __name__ == "__main__":
    main()
