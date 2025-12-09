#!/bin/bash

# Script Exercice 20 :
# Lance les tests (lint + tests Django) sous différentes versions de Python et Django.
# Nécessite d'avoir les différents interpréteurs Python installés localement
# (python3.13, python3.9, python2.7, etc.).

set -e

PYTHON_VERSIONS=("3.13" "3.9" "2.7")
DJANGO_VERSIONS=("5" "4" "3")

echo "🚀 Démarrage de la matrice de tests qualité..."
echo

for py in "${PYTHON_VERSIONS[@]}"; do
  PY_BIN="python${py}"

  if ! command -v "$PY_BIN" >/dev/null 2>&1; then
    echo "⚠️  Python ${py} introuvable sur cette machine, on saute cette version."
    echo
    continue
  fi

  for dj in "${DJANGO_VERSIONS[@]}"; do

    echo "=============================================="
    echo "🔧 Tests pour Python ${py} / Django ${dj}"
    echo "=============================================="

    # Compatibilité simplifiée (réaliste, mais pédagogique)
    DJANGO_SPEC=""
    case "$dj" in
      "5")
        # Django 5.x : Python >= 3.10
        if [[ "$py" == "3.13" ]]; then
          DJANGO_SPEC="django>=5.0,<6.0"
        else
          echo "⏭️  Django 5 n'est pas compatible avec Python ${py}, on saute."
          echo
          continue
        fi
        ;;
      "4")
        # Django 4.x : Python >= 3.8
        if [[ "$py" == "3.13" || "$py" == "3.9" ]]; then
          DJANGO_SPEC="django>=4.0,<5.0"
        else
          echo "⏭️  Django 4 n'est pas compatible avec Python ${py}, on saute."
          echo
          continue
        fi
        ;;
      "3")
        # Django 3.x : Python 3.6–3.10 (on utilise 3.9 ici)
        if [[ "$py" == "3.9" ]]; then
          DJANGO_SPEC="django>=3.0,<4.0"
        else
          # Si tu as un vieux Python 2.7 + vieux Django chez toi, tu peux adapter ici
          echo "⏭️  Django 3 n'est pas prévu pour Python ${py} dans ce script, on saute."
          echo
          continue
        fi
        ;;
    esac

    export PIPENV_IGNORE_VIRTUALENVS=1

    # On recrée un environnement pipenv dédié à cette combinaison
    echo "🧹 Suppression de l'environnement pipenv existant (s'il y en a un)..."
    pipenv --rm >/dev/null 2>&1 || true

    echo "🐍 Création de l'environnement pipenv avec ${PY_BIN}..."
    pipenv --python "$PY_BIN"

    echo "📦 Installation de Django (${DJANGO_SPEC}) + dépendances du projet..."
    pipenv install "$DJANGO_SPEC"
    pipenv install --dev ruff coverage

    echo "🔍 Lancement du linter Ruff..."
    pipenv run ruff check .

    echo "🧪 Lancement des tests Django..."
    pipenv run python manage.py test

    echo "✅ Succès pour Python ${py} / Django ${dj}"
    echo
  done
done

echo "🎉 Matrice de tests terminée."

