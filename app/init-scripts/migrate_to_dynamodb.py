"""
Migration script: Seed data from telemedicine_db.sql → DynamoDB afiya-data.

Run:  cd /home/abdia/telemedecine-api/app && PYTHONPATH=. python init-scripts/migrate_to_dynamodb.py
"""

import uuid
import boto3
from datetime import datetime, timezone
from core.config import settings

TABLE_NAME = "afiya-data"

# ──────────────────────────────────────────────
# Seed data extracted from telemedicine_db.sql
# ──────────────────────────────────────────────

SEED_DATA = {
    "sexe": [
        {"libelle": "Masculin", "code": "M"},
        {"libelle": "Feminin", "code": "F"},
        {"libelle": "Autre", "code": "AUTRE"},
    ],
    "statut": [
        {"libelle": "Actif", "code": "ACTIF"},
        {"libelle": "Inactif", "code": "INACTIF"},
        {"libelle": "Suspendu", "code": "SUSPENDU"},
        {"libelle": "En attente", "code": "EN_ATTENTE"},
    ],
    "specialite": [
        {"libelle": "Medecine Generale", "code": "GENERALISTE", "description": None},
        {"libelle": "Cardiologie", "code": "CARDIOLOGUE", "description": None},
        {"libelle": "Pediatrie", "code": "PEDIATRE", "description": None},
        {"libelle": "Dermatologie", "code": "DERMATOLOGUE", "description": None},
        {"libelle": "Gynecologie", "code": "GYNECOLOGUE", "description": None},
    ],
    "emetteur": [
        {"type": "Patient", "code": "PATIENT"},
        {"type": "Medecin", "code": "MEDECIN"},
        {"type": "Bot", "code": "BOT"},
        {"type": "Systeme", "code": "SYSTEM"},
    ],
    "statut_conversation": [
        {"libelle": "Bot actif", "code": "BOT_ACTIVE"},
        {"libelle": "Medecin actif", "code": "HUMAN_ACTIVE"},
        {"libelle": "Fermee", "code": "CLOSED"},
        {"libelle": "En attente", "code": "PENDING"},
    ],
    "statut_livraison": [
        {"libelle": "Envoye", "code": "SENT"},
        {"libelle": "Delivre", "code": "DELIVERED"},
        {"libelle": "Lu", "code": "READ"},
        {"libelle": "Echec", "code": "FAILED"},
    ],
    "statut_paiement": [
        {"libelle": "En attente", "code": "PENDING"},
        {"libelle": "Paye", "code": "PAID"},
        {"libelle": "Echoue", "code": "FAILED"},
        {"libelle": "Rembourse", "code": "REFUNDED"},
        {"libelle": "Annule", "code": "CANCELLED"},
    ],
    "operateur": [
        {"nom": "MTN Mobile Money", "code": "MTN", "prefixe": "67"},
        {"nom": "Orange Money", "code": "ORANGE", "prefixe": "69"},
        {"nom": "CinetPay", "code": "CINETPAY", "prefixe": None},
    ],
    "statut_consultation": [
        {"libelle": "En attente", "code": "EN_ATTENTE"},
        {"libelle": "En cours", "code": "EN_COURS"},
        {"libelle": "Terminee", "code": "TERMINEE"},
        {"libelle": "Annulee", "code": "ANNULEE"},
    ],
}


def get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


def seed_entity(table, entity_type: str, records: list, start_id: int = 1):
    """
    Insert seed records for one entity type into DynamoDB.
    Each record gets PK=ENTITYTYPE#<id>, SK=METADATA#<uuid>, EntityType=<type>.
    Records get sequential IDs starting from start_id (matching PostgreSQL IDs).
    """
    count = 0
    for i, record in enumerate(records, start=start_id):
        pk = f"{entity_type.upper()}#{i}"
        sk = f"METADATA#seed-{uuid.uuid4().hex[:8]}"
        item = {
            "PK": pk,
            "SK": sk,
            "EntityType": entity_type,
            "EntityId": str(i),
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        item.update({k: v for k, v in record.items() if v is not None})
        table.put_item(Item=item)
        count += 1
    return count


def main():
    print(f"Connecting to DynamoDB table: {TABLE_NAME}")
    print(f"Region: {settings.AWS_REGION}")

    table = get_table()
    total = 0

    for entity_type, records in SEED_DATA.items():
        count = seed_entity(table, entity_type, records)
        total += count
        print(f"  {entity_type}: {count} items inserted")

    print(f"\nDone. {total} items migrated to '{TABLE_NAME}'.")


if __name__ == "__main__":
    main()
