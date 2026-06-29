"""
DynamoDB table schema for the Afiya telemedicine platform.

Single-table design — ALL 29 entities live in ONE table:
  29 entities = 25 business + 4 workflow tables, distinguished by EntityType.

  Access patterns:
    PK = ENTITYTYPE#<id>     → get by ID (HASH key)
    SK = METADATA | STEP#<n> | STEP_EXEC#<id>  → sort/organize items

  Business entities (25):
    USER#<id>         │ METADATA          sexe, statut, specialite, emetteur,
    PAIEMENT#<id>     │ METADATA          operateur, statut_conversation, statut_paiement,
    CONSULTATION#<id> │ METADATA          statut_livraison, statut_consultation, user,
    CONVERSATION#<id> │ METADATA          user_session, user_specialite, dossier_medical,
    MESSAGE#<id>      │ METADATA          conversation, message, consultation, paiement,
    NOTIFICATION#<id> │ METADATA          metric, avis_consultation, medecin_disponibilite,
    DOCUMENT#<id>     │ METADATA          images_consultation, document, notification,
    AUDIT_LOG#<id>    │ METADATA          ordonnance_template, audit_log
    ...

  Workflow entities (4):
    WORKFLOW#<id>      │ METADATA#<id>
    WORKFLOW#<wf>      │ STEP#<order>          GSI1PK=WORKFLOW#<wf>
    EXECUTION#<id>     │ METADATA#<id>         GSI1PK=WORKFLOW#<wf>  GSI1SK=STARTED#<ts>
    EXECUTION#<exec>   │ STEP_EXEC#<step_id>   GSI1PK=WORKFLOW#<wf>

  GSIs:
    EntityTypeIndex → list all items of a type (EntityType=HASH, PK=RANGE)
    GSI1            → group workflow steps/executions by workflow (GSI1PK=HASH, GSI1SK=RANGE)
"""

import boto3
from core.config import settings

TABLE_NAME = "afiya-data"


def create_dynamodb_table():
    client = boto3.client(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )

    try:
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "EntityType", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "EntityTypeIndex",
                    "KeySchema": [
                        {"AttributeName": "EntityType", "KeyType": "HASH"},
                        {"AttributeName": "PK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"DynamoDB table '{TABLE_NAME}' created successfully.")
    except client.exceptions.ResourceInUseException:
        print(f"DynamoDB table '{TABLE_NAME}' already exists.")


if __name__ == "__main__":
    create_dynamodb_table()
