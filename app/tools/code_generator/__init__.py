"""
tools/code_generator
--------------------
Générateur automatique de CRUD pour l'API Télémédecine.

Génère les couches suivantes à partir du schéma PostgreSQL :
  Controller → Service → Repository → Mapper → Entity / Model + Schemas

Usage rapide :
    # En CLI
    python -m app.tools.code_generator.generate --list
    python -m app.tools.code_generator.generate --table ma_nouvelle_table

    # En Python
    from app.tools.code_generator import generate_crud
    generate_crud("ma_nouvelle_table")
"""

from tools.code_generator.db_inspector import DBInspector
from tools.code_generator.file_writer import FileWriter
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parents[2]  # app/


def generate_crud(
    table_name: str,
    *,
    output: str = None,
    host: str = None,
    port: int = None,
    user: str = None,
    password: str = None,
    dbname: str = None,
    schema: str = "public",
    dry_run: bool = False,
) -> int:
    """
    Génère les fichiers CRUD complets pour une table PostgreSQL.

    Args:
        table_name: Nom de la table à générer
        output:     Répertoire racine app/ (défaut: auto-détecté)
        host:       Hôte PostgreSQL (défaut: DB_HOST ou localhost)
        port:       Port PostgreSQL (défaut: DB_PORT ou 5432)
        user:       Utilisateur (défaut: DB_USER ou postgres)
        password:   Mot de passe (défaut: DB_PASSWORD ou postgres)
        dbname:     Nom de la base (défaut: DB_NAME ou telemedecine_db)
        schema:     Schéma PostgreSQL (défaut: public)
        dry_run:    Si True, n'écrit aucun fichier

    Returns:
        Nombre de fichiers générés

    Example:
        >>> from app.tools.code_generator import generate_crud
        >>> generate_crud("prescription")
        14
    """
    inspector = DBInspector(
        host=host, port=port, user=user,
        password=password, dbname=dbname, schema=schema
    )
    writer = FileWriter(project_root=output or str(_APP_ROOT))

    with inspector:
        metadata = inspector.get_table_metadata(table_name)
        if dry_run:
            return 7  # 7 couches générées par table
        created = writer.write_all(table_name, metadata)
        return len(created)


__all__ = ["generate_crud", "DBInspector", "FileWriter"]
