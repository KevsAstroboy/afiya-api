"""
db_inspector.py
---------------
Connexion synchrone à PostgreSQL pour lire le schéma des tables
et produire les métadonnées nécessaires à la génération de code.

Usage:
    from app.tools.code_generator.db_inspector import DBInspector

    inspector = DBInspector()
    tables = inspector.list_tables()
    columns = inspector.get_columns("sexe")
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Mapping PostgreSQL type -> (SQLAlchemy type, Python type)
PG_TYPE_MAP: Dict[str, Tuple[str, str]] = {
    # Entiers
    "bigint":            ("BigInteger", "int"),
    "integer":           ("Integer",    "int"),
    "smallint":          ("Integer",    "int"),
    "bigserial":         ("BigInteger", "int"),
    "serial":            ("Integer",    "int"),

    # Texte
    "character varying": ("String",     "str"),
    "varchar":           ("String",     "str"),
    "character":         ("String",     "str"),
    "char":              ("String",     "str"),
    "text":              ("Text",       "str"),
    "citext":            ("Text",       "str"),

    # Booléen
    "boolean":           ("Boolean",    "bool"),

    # Numériques
    "numeric":           ("Numeric",    "float"),
    "decimal":           ("Numeric",    "float"),
    "real":              ("Float",      "float"),
    "double precision":  ("Float",      "float"),

    # Date / Time
    "timestamp without time zone": ("DateTime", "datetime"),
    "timestamp with time zone":    ("DateTime", "datetime"),
    "timestamp":                   ("DateTime", "datetime"),
    "date":                        ("Date",     "date"),
    "time without time zone":      ("Time",     "str"),
    "time":                        ("Time",     "str"),

    # JSON
    "json":              ("JSON",   "dict"),
    "jsonb":             ("JSON",   "dict"),

    # Autres
    "uuid":              ("String(36)", "str"),
    "bytea":             ("LargeBinary", "bytes"),
}

# Champs d'audit à ignorer dans les colonnes métier
AUDIT_FIELDS = {
    "created_at", "updated_at", "deleted_at",
    "created_by", "updated_by", "deleted_by",
    "is_deleted", "deletion_reason"
}


class ColumnInfo:
    """Représente une colonne de table PostgreSQL"""

    def __init__(self, raw: Dict[str, Any]):
        self.name: str = raw["column_name"]
        self.pg_type: str = raw["udt_name"] or raw["data_type"]
        self.data_type: str = raw["data_type"]
        self.is_nullable: bool = raw["is_nullable"] == "YES"
        self.column_default: Optional[str] = raw.get("column_default")
        self.char_max_length: Optional[int] = raw.get("character_maximum_length")
        self.numeric_precision: Optional[int] = raw.get("numeric_precision")
        self.numeric_scale: Optional[int] = raw.get("numeric_scale")

        # Résolution des types
        sa_type, py_type = self._resolve_types()
        self.sa_type: str = sa_type
        self.py_type: str = py_type

        # Clé étrangère (renseignée après par DBInspector)
        self.fk_table: Optional[str] = None
        self.fk_column: Optional[str] = None

        # Contraintes (renseignées après)
        self.is_primary_key: bool = False
        self.is_unique: bool = False

    def _resolve_types(self) -> Tuple[str, str]:
        # Cherche d'abord par data_type complet, puis udt_name
        for key in [self.data_type, self.pg_type]:
            if key in PG_TYPE_MAP:
                sa, py = PG_TYPE_MAP[key]
                # Ajouter la longueur pour les varchar
                if sa == "String" and self.char_max_length:
                    sa = f"String({self.char_max_length})"
                # Ajouter précision pour Numeric
                if sa == "Numeric" and self.numeric_precision:
                    scale = self.numeric_scale or 2
                    sa = f"Numeric({self.numeric_precision}, {scale})"
                return sa, py

        # Fallback
        logger.warning(f"Type inconnu: {self.data_type}/{self.pg_type}, fallback Text")
        return "Text", "str"

    def to_sa_column(self) -> str:
        """Génère la ligne Column(...) pour l'entity SQLAlchemy"""
        args = [self.sa_type]

        if self.fk_table and self.fk_column:
            args.append(f"ForeignKey('public.{self.fk_table}.{self.fk_column}')")

        kwargs = []
        kwargs.append(f"nullable={not self.is_nullable}")

        if self.is_unique and not self.is_primary_key:
            kwargs.append("unique=True")

        if self.column_default and "nextval" not in str(self.column_default):
            if self.column_default == "now()":
                kwargs.append("server_default=func.now()")
            elif self.column_default in ("true", "false"):
                kwargs.append(f"default={self.column_default.capitalize()}")
            elif self.column_default.startswith("'") and self.column_default.endswith("'::"):
                val = self.column_default.split("'")[1]
                kwargs.append(f"default='{val}'")

        return f"    {self.name} = Column({', '.join(args)}, {', '.join(kwargs)})"

    @property
    def is_audit(self) -> bool:
        return self.name in AUDIT_FIELDS

    @property
    def pydantic_field(self) -> str:
        """Génère le champ pour les schemas Pydantic"""
        if self.is_nullable:
            return f"    {self.name}: Optional[{self.py_type}] = None"
        return f"    {self.name}: {self.py_type}"


class DBInspector:
    """
    Inspecte le schéma PostgreSQL pour extraire les métadonnées des tables.

    Utilise psycopg2 (synchrone) pour éviter la complexité asyncio
    dans un script de génération de code.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        schema: str = "public"
    ):
        # Priorité: paramètres > variables d'environnement > valeurs par défaut
        self.host     = host     or os.getenv("DB_HOST",     "localhost")
        self.port     = port     or int(os.getenv("DB_PORT", "5432"))
        self.user     = user     or os.getenv("DB_USER",     "postgres")
        self.password = password or os.getenv("DB_PASSWORD", "postgres")
        self.dbname   = dbname   or os.getenv("DB_NAME",     "telemedecine_db")
        self.schema   = schema

        self._conn = None

    def connect(self):
        """Établit la connexion à PostgreSQL"""
        try:
            import psycopg2
            self._conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            logger.info(f"Connecté à {self.dbname}@{self.host}:{self.port}")
        except ImportError:
            raise RuntimeError(
                "psycopg2 requis: pip install psycopg2-binary"
            )
        except Exception as e:
            raise RuntimeError(f"Erreur de connexion PostgreSQL: {e}")

    def disconnect(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def _cursor(self):
        if not self._conn:
            self.connect()
        return self._conn.cursor()

    def list_tables(self, exclude_audit_log: bool = False) -> List[str]:
        """Liste toutes les tables du schéma"""
        cur = self._cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (self.schema,))
        tables = [row[0] for row in cur.fetchall()]
        if exclude_audit_log:
            tables = [t for t in tables if t != "audit_log"]
        return tables

    def get_columns(self, table_name: str) -> List[ColumnInfo]:
        """Retourne les colonnes d'une table (sans id ni audit fields)"""
        cur = self._cursor()
        cur.execute("""
            SELECT
                c.column_name,
                c.data_type,
                c.udt_name,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale
            FROM information_schema.columns c
            WHERE c.table_schema = %s
              AND c.table_name   = %s
            ORDER BY c.ordinal_position
        """, (self.schema, table_name))

        rows = cur.fetchall()
        columns = []
        for row in rows:
            col = ColumnInfo({
                "column_name":              row[0],
                "data_type":                row[1],
                "udt_name":                 row[2],
                "is_nullable":              row[3],
                "column_default":           row[4],
                "character_maximum_length": row[5],
                "numeric_precision":        row[6],
                "numeric_scale":            row[7],
            })
            # Exclure id (géré séparément) et audit fields
            if col.name == "id" or col.name in AUDIT_FIELDS:
                continue
            columns.append(col)

        # Enrichir avec FK et contraintes uniques
        self._enrich_foreign_keys(table_name, columns)
        self._enrich_unique_constraints(table_name, columns)

        return columns

    def _enrich_foreign_keys(self, table_name: str, columns: List[ColumnInfo]):
        """Ajoute les informations de clé étrangère aux colonnes"""
        cur = self._cursor()
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name  AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
               AND tc.table_schema    = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
               AND ccu.table_schema    = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema    = %s
              AND tc.table_name      = %s
        """, (self.schema, table_name))

        fk_map = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
        for col in columns:
            if col.name in fk_map:
                col.fk_table, col.fk_column = fk_map[col.name]

    def _enrich_unique_constraints(self, table_name: str, columns: List[ColumnInfo]):
        """Marque les colonnes avec contrainte UNIQUE"""
        cur = self._cursor()
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
               AND tc.table_schema    = kcu.table_schema
            WHERE tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
              AND tc.table_schema = %s
              AND tc.table_name   = %s
        """, (self.schema, table_name))

        unique_cols = {row[0] for row in cur.fetchall()}
        for col in columns:
            if col.name in unique_cols:
                col.is_unique = True

    def has_audit_fields(self, table_name: str) -> bool:
        """Vérifie si la table possède les champs d'audit (is_deleted, etc.)"""
        cur = self._cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name   = %s
              AND column_name  = 'is_deleted'
        """, (self.schema, table_name))
        return cur.fetchone()[0] > 0

    def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """
        Retourne toutes les métadonnées d'une table :
        - columns: List[ColumnInfo]
        - has_audit: bool
        - class_name: str (PascalCase)
        - url_slug: str (kebab-case)
        """
        columns = self.get_columns(table_name)
        has_audit = self.has_audit_fields(table_name)

        class_name = "".join(w.capitalize() for w in table_name.split("_"))
        url_slug = table_name.replace("_", "-")

        return {
            "table_name":  table_name,
            "class_name":  class_name,
            "url_slug":    url_slug,
            "columns":     columns,
            "has_audit":   has_audit,
        }
