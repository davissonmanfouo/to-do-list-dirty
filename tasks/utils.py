import json
from pathlib import Path

from .models import Task


def import_tasks_from_dataset(dataset_path: Path | None = None) -> int:
    """
    Importe des tâches depuis un fichier JSON de dataset.
    Retourne le nombre de tâches créées.
    """
    if dataset_path is None:
        # dataset.json à la racine du projet
        base_dir = Path(__file__).resolve().parent.parent
        dataset_path = base_dir / "dataset.json"

    with dataset_path.open(encoding="utf-8") as f:
        data = json.load(f)

    created_count = 0
    for item in data:
        Task.objects.create(
            title=item["title"],
            complete=item.get("complete", False),
        )
        created_count += 1

    return created_count
