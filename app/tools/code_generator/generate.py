#!/usr/bin/env python3
"""
generate.py
-----------
Script principal du générateur CRUD pour l'API Télémédecine.

Se connecte à PostgreSQL, lit le schéma des tables et génère
automatiquement tous les fichiers CRUD en respectant l'architecture :

    Controller → Service → Repository → Mapper → Entity/Model

Usage:
    # Générer TOUTES les tables
    python -m app.tools.code_generator.generate

    # Générer une table spécifique
    python -m app.tools.code_generator.generate --table sexe

    # Générer plusieurs tables
    python -m app.tools.code_generator.generate --table sexe statut specialite

    # Lister les tables disponibles
    python -m app.tools.code_generator.generate --list

    # Spécifier une connexion DB personnalisée
    python -m app.tools.code_generator.generate \\
        --host localhost --port 5432 \\
        --user postgres --password secret \\
        --dbname telemedecine_db \\
        --table sexe

Variables d'environnement supportées (priorité sur les valeurs par défaut) :
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Ajout du root du projet au path pour les imports
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # remonte jusqu'à telemedecine-api
APP_ROOT = PROJECT_ROOT / "app"
sys.path.insert(0, str(PROJECT_ROOT))

from tools.code_generator.db_inspector import DBInspector
from tools.code_generator.file_writer import FileWriter

# ------------------------------------------------------------------ #
#  Configuration du logging                                            #
# ------------------------------------------------------------------ #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("code_generator")


# ------------------------------------------------------------------ #
#  CLI                                                                 #
# ------------------------------------------------------------------ #

def parse_args():
    parser = argparse.ArgumentParser(
        description="Générateur CRUD pour l'API Télémédecine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Tables
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--table", "-t",
        nargs="+",
        metavar="TABLE",
        help="Nom(s) de table(s) à générer (ex: sexe statut)"
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lister toutes les tables disponibles"
    )

    # Connexion DB
    parser.add_argument("--host",     default=None, help="Hôte PostgreSQL (défaut: DB_HOST ou localhost)")
    parser.add_argument("--port",     type=int, default=None, help="Port PostgreSQL (défaut: DB_PORT ou 5432)")
    parser.add_argument("--user",     default=None, help="Utilisateur (défaut: DB_USER ou postgres)")
    parser.add_argument("--password", default=None, help="Mot de passe (défaut: DB_PASSWORD ou postgres)")
    parser.add_argument("--dbname",   default=None, help="Nom de la base (défaut: DB_NAME ou telemedecine_db)")
    parser.add_argument("--schema",   default="public", help="Schéma PostgreSQL (défaut: public)")

    # Options
    parser.add_argument(
        "--output", "-o",
        default=str(APP_ROOT),
        help=f"Répertoire racine du projet (défaut: {APP_ROOT})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche ce qui serait généré sans écrire les fichiers"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Écrase les fichiers existants sans confirmation"
    )

    return parser.parse_args()


# ------------------------------------------------------------------ #
#  Logique principale                                                  #
# ------------------------------------------------------------------ #

def list_tables(inspector: DBInspector):
    """Affiche toutes les tables disponibles"""
    tables = inspector.list_tables()
    print(f"\n📋 Tables disponibles dans le schéma '{inspector.schema}' ({len(tables)}) :\n")
    for t in tables:
        has_audit = inspector.has_audit_fields(t)
        audit_label = "✅ audit" if has_audit else "⚠️  sans audit"
        print(f"  • {t:<35} [{audit_label}]")
    print()


def generate_table(
    table_name: str,
    inspector: DBInspector,
    writer: FileWriter,
    dry_run: bool = False
) -> int:
    """Génère les fichiers CRUD pour une table. Retourne le nb de fichiers créés."""
    logger.info(f"🔍 Analyse de la table '{table_name}'...")

    try:
        metadata = inspector.get_table_metadata(table_name)
    except Exception as e:
        logger.error(f"Erreur lors de l'inspection de '{table_name}': {e}")
        return 0

    columns = metadata["columns"]
    if not columns:
        logger.warning(f"  ⚠️  Aucune colonne trouvée pour '{table_name}' (après exclusion id + audit)")

    cn = metadata["class_name"]
    has_audit = metadata["has_audit"]

    logger.info(f"  → {len(columns)} colonnes | class: {cn} | audit: {has_audit}")
    for col in columns:
        fk_info = f" → FK({col.fk_table}.{col.fk_column})" if col.fk_table else ""
        unique_info = " [UNIQUE]" if col.is_unique else ""
        nullable_info = "nullable" if col.is_nullable else "NOT NULL"
        logger.info(f"     • {col.name:<30} {col.sa_type:<20} {nullable_info}{fk_info}{unique_info}")

    if dry_run:
        logger.info(f"  [DRY-RUN] Fichiers qui seraient générés pour '{table_name}':")
        for layer in ["entity", "model", "mapper", "repository", "schemas", "service", "controller"]:
            logger.info(f"     • {layer}")
        return 7

    try:
        created = writer.write_all(table_name, metadata)
        logger.info(f"  ✅ {len(created)} fichiers générés pour '{table_name}'")
        return len(created)
    except Exception as e:
        logger.error(f"  ❌ Erreur lors de la génération de '{table_name}': {e}")
        raise


def main():
    args = parse_args()

    # Connexion DB
    inspector = DBInspector(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        dbname=args.dbname,
        schema=args.schema
    )

    try:
        inspector.connect()
    except RuntimeError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)

    writer = FileWriter(project_root=args.output)

    try:
        # Mode listing
        if args.list:
            list_tables(inspector)
            return

        # Sélection des tables
        if args.table:
            tables = args.table
        else:
            # Toutes les tables
            tables = inspector.list_tables()
            logger.info(f"🗂️  {len(tables)} tables trouvées, génération en cours...")

        # Validation des tables
        available = set(inspector.list_tables())
        invalid = [t for t in tables if t not in available]
        if invalid:
            logger.error(f"❌ Tables introuvables : {invalid}")
            logger.info(f"   Tables disponibles : {sorted(available)}")
            sys.exit(1)

        # Génération
        print(f"\n{'='*60}")
        print(f"  🚀 Génération CRUD - {len(tables)} table(s)")
        print(f"  📁 Output: {args.output}")
        if args.dry_run:
            print("  🔍 MODE DRY-RUN - aucun fichier ne sera écrit")
        print(f"{'='*60}\n")

        total_files = 0
        errors = []

        for table in tables:
            try:
                total_files += generate_table(table, inspector, writer, dry_run=args.dry_run)
            except Exception as e:
                errors.append((table, str(e)))

        # Résumé
        print(f"\n{'='*60}")
        print(f"  ✅ Terminé : {total_files} fichiers {'(simulés)' if args.dry_run else 'générés'}")
        print(f"  📊 Tables traitées : {len(tables) - len(errors)}/{len(tables)}")
        if errors:
            print(f"  ❌ Erreurs ({len(errors)}) :")
            for table, err in errors:
                print(f"     • {table}: {err}")
        print(f"{'='*60}\n")

    finally:
        inspector.disconnect()


if __name__ == "__main__":
    main()
