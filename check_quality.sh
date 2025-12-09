#!/bin/bash

echo "🔍 Checking code quality with Ruff..."
pipenv run ruff check .

# Uncomment plus tard si tu veux exécuter les tests :
# echo "🧪 Running tests..."
# pipenv run python manage.py test

echo " Quality check completed."
