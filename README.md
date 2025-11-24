# to-do-list app
cat > README.md << 'EOF'
# Todo-list Application

Application de gestion de tâches développée avec Django.

## Gestion des versions

Ce projet utilise le **Semantic Versioning** (SemVer) : https://semver.org/lang/fr/

Format : `MAJOR.MINOR.PATCH`

- **MAJOR** : changements incompatibles avec les versions précédentes
- **MINOR** : ajout de fonctionnalités rétrocompatibles
- **PATCH** : corrections de bugs rétrocompatibles

Exemples :
- `1.0.0` → `1.0.1` : correction de bug
- `1.0.0` → `1.1.0` : nouvelle fonctionnalité
- `1.0.0` → `2.0.0` : changement majeur cassant la compatibilité

## Gestion des commits

Ce projet suit la convention **Conventional Commits** : https://www.conventionalcommits.org/en/v1.0.0/

Format : `<type>(<scope>): <description>`

### Types de commits :

- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation uniquement
- `style:` Formatage, virgules manquantes, etc. (pas de changement de code)
- `refactor:` Refactoring de code (ni feat ni fix)
- `test:` Ajout ou modification de tests
- `chore:` Tâches de maintenance (build, config, etc.)

### Exemples :
```
feat(tasks): ajout de la fonctionnalité de filtrage par date
fix(database): correction du bug de sauvegarde des tâches
docs(readme): mise à jour de la documentation d'installation
test(tasks): ajout des tests pour la suppression de tâches
chore(build): mise à jour du script de build vers 1.1.0
```

## Workflow Git

### Branches principales :
- `main` : branche de production (versions stables uniquement)
- `dev-quality-system` : branche de développement pour les améliorations qualité

### Process de release :
1. Développer sur la branche `dev-quality-system`
2. Utiliser le script de build : `./build.sh version=X.Y.Z`
3. Merger vers `main` quand la version est stable
4. Le tag de version est créé automatiquement

## Installation
```bash
# Cloner le projet
git clone [URL_DU_REPO]

# Installer les dépendances
pip install django

# Lancer l'application
python manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000

## Build

Pour créer une nouvelle version :
```bash
./build.sh version=X.Y.Z
```

Cela va automatiquement :
- Mettre à jour le numéro de version
- Créer un commit
- Créer un tag Git
- Générer une archive `todolist-X.Y.Z.zip`

EOF