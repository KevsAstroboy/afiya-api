# 🛠️ Code Generator - Télémédecine API

Générateur automatique de CRUD qui se connecte à PostgreSQL, lit le schéma
réel de tes tables et produit tous les fichiers de ton architecture en une commande.

## Architecture générée

Pour chaque table, le générateur crée **7 couches** :

```
app/
├── models/{table}/
│   ├── entity/
│   │   ├── {table}_entity.py     ← SQLAlchemy ORM
│   │   └── {table}_model.py      ← Dataclass domaine
│   ├── mapper/
│   │   └── {table}_mapper.py     ← Entity ↔ Domain
│   ├── repository/
│   │   └── {table}_repository.py ← CRUD async (accès DB)
│   └── {table}_schemas.py        ← Pydantic (Create/Update/Response)
├── services/{table}/
│   └── {table}_service.py        ← Logique métier
└── controllers/api/{table}/controller/
    └── {table}_controller.py     ← Endpoints FastAPI
```

**Flux d'appel :**
```
HTTP Request
    → Controller  (validation Pydantic, routing)
        → Service     (logique métier)
            → Repository  (accès DB via SQLAlchemy)
                → Mapper  (Entity ↔ Domain)
                    → Entity  (SQLAlchemy model)
```

## Installation

```bash
# psycopg2 requis pour la connexion synchrone au moment de la génération
pip install psycopg2-binary
```

## Usage CLI

```bash
# Depuis la racine du projet (telemedecine-api/)
cd telemedecine-api

# Lister toutes les tables disponibles
python -m app.tools.code_generator.generate --list

# Générer UNE table
python -m app.tools.code_generator.generate --table prescription

# Générer PLUSIEURS tables
python -m app.tools.code_generator.generate --table prescription dosage protocole

# Générer TOUTES les tables
python -m app.tools.code_generator.generate

# Simuler sans écrire (dry-run)
python -m app.tools.code_generator.generate --table prescription --dry-run

# Connexion DB personnalisée
python -m app.tools.code_generator.generate \
    --host localhost \
    --port 5432 \
    --user postgres \
    --password monmotdepasse \
    --dbname telemedecine_db \
    --table prescription
```

## Variables d'environnement

Le générateur lit automatiquement les variables d'environnement de ton `.env` :

| Variable      | Défaut          | Description           |
|---------------|-----------------|-----------------------|
| `DB_HOST`     | `localhost`     | Hôte PostgreSQL       |
| `DB_PORT`     | `5432`          | Port PostgreSQL        |
| `DB_USER`     | `postgres`      | Utilisateur           |
| `DB_PASSWORD` | `postgres`      | Mot de passe          |
| `DB_NAME`     | `telemedecine_db` | Nom de la base      |

## Usage Python

```python
from app.tools.code_generator import generate_crud

# Simple
nb_fichiers = generate_crud("prescription")
print(f"{nb_fichiers} fichiers générés")

# Avec options
generate_crud(
    "prescription",
    host="localhost",
    user="postgres",
    password="secret",
    dry_run=False
)
```

## Workflow pour une nouvelle table

1. **Créer la table SQL** dans `app/init-scripts/telemedicine_db.sql`

   ```sql
   CREATE TABLE IF NOT EXISTS public.prescription (
       id BIGSERIAL PRIMARY KEY,
       consultation_id BIGINT NOT NULL REFERENCES public.consultation(id),
       medecin_id      BIGINT NOT NULL REFERENCES public.user(id),
       contenu         TEXT   NOT NULL,
       date_emission   TIMESTAMP NOT NULL DEFAULT NOW(),
       valide_jusqu    TIMESTAMP,
       -- Champs d'audit
       created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
       updated_at      TIMESTAMP,
       deleted_at      TIMESTAMP,
       created_by      BIGINT,
       updated_by      BIGINT,
       deleted_by      BIGINT,
       is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
       deletion_reason TEXT
   );
   ```

2. **Appliquer le schéma** en base

   ```bash
   psql -U postgres -d telemedecine_db -f app/init-scripts/telemedicine_db.sql
   ```

3. **Générer le CRUD**

   ```bash
   python -m app.tools.code_generator.generate --table prescription
   ```

4. **Vérifier les fichiers** générés — le router est découvert automatiquement
   par `discover_and_include_routers()` dans `utilities/utils.py`.

5. **Ajouter la logique métier** dans `services/prescription/prescription_service.py`

## Fonctionnalités du générateur

- ✅ Lecture automatique des colonnes depuis `information_schema`
- ✅ Détection des **clés étrangères** → `ForeignKey('public.table.id')`
- ✅ Détection des **contraintes UNIQUE**
- ✅ Détection des **valeurs par défaut** (now(), true/false, strings)
- ✅ Mapping PostgreSQL → SQLAlchemy → Python automatique
- ✅ Gestion des types : varchar(N), numeric(p,s), text, boolean, json/jsonb, timestamp, time...
- ✅ Champs d'**audit automatiques** (created_at, is_deleted, etc.) si présents
- ✅ **Soft delete** si `is_deleted` présent, sinon hard delete
- ✅ Mode **dry-run** pour prévisualiser
- ✅ Support multi-tables en une commande

## Mapping des types

| PostgreSQL             | SQLAlchemy          | Python      |
|------------------------|---------------------|-------------|
| bigint / bigserial     | BigInteger          | int         |
| integer / serial       | Integer             | int         |
| varchar(N)             | String(N)           | str         |
| text                   | Text                | str         |
| boolean                | Boolean             | bool        |
| numeric(p, s)          | Numeric(p, s)       | float       |
| timestamp              | DateTime            | datetime    |
| time                   | Time                | str         |
| json / jsonb           | JSON                | dict        |
| uuid                   | String(36)          | str         |

## Templates

Les templates `.tpl` dans `templates/` servent de **documentation de référence**
pour comprendre la structure attendue. La génération réelle est faite par
`FileWriter` qui construit le contenu programmatiquement pour plus de flexibilité.

| Template                    | Description                        |
|-----------------------------|------------------------------------|
| `entity_template.py.tpl`    | Entity SQLAlchemy avec audit       |
| `entity_no_audit_template.py.tpl` | Entity sans soft-delete      |
| `model_template.py.tpl`     | Dataclass domaine                  |
| `mapper_template.py.tpl`    | Mapper Entity ↔ Domain             |
| `repository_template.py.tpl` | Repository async CRUD             |
| `service_template.py.tpl`   | Service (logique métier)           |
| `schemas_template.py.tpl`   | Schemas Pydantic                   |
| `controller_template.py.tpl` | Endpoints FastAPI                 |
