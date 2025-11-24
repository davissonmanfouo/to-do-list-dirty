#!/bin/bash

# Script de build automatique pour Todo-list app
# Usage: ./build.sh version=1.0.1

# Extraction du numéro de version
VERSION=${1#Version=}

if [ -z "$VERSION" ]; then
    echo "Erreur: Vous devez spécifier une version"
    echo "Usage: ./build.sh version=X.Y.Z"
    exit 1
fi

echo "🚀 Build de la version $VERSION"

# 1. Mise à jour de la variable VERSION dans settings.py
echo "📝 Mise à jour de la version dans settings.py..."
sed -i "s/VERSION = \".*\"/VERSION = \"$VERSION\"/" */settings.py

# 2. Commit des changements
git add */settings.py
git commit -m "chore: bump version to $VERSION"

# 3. Création du tag
echo "🏷️  Création du tag $VERSION..."
git tag -a "$VERSION" -m "Version $VERSION"

# 4. Génération de la tarball
echo "📦 Génération de l'archive..."
git archive --format=zip --output="todolist-$VERSION.zip" HEAD

echo "✅ Build terminé! Archive: todolist-$VERSION.zip"