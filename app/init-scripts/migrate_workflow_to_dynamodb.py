"""
Migration script: Insert workflow wf-patient-collecte + 12 steps into DynamoDB afiya-data.

Run:  cd /home/abdia/telemedecine-api/app && PYTHONPATH=. python init-scripts/migrate_workflow_to_dynamodb.py
"""

import uuid
import boto3
from datetime import datetime, timezone
from core.config import settings

TABLE_NAME = "afiya-data"
WORKFLOW_ID = "wf-patient-collecte"

STEPS = [
    {
        "id": "step-accueil",
        "name": "accueil",
        "step_order": 1,
        "step_type": "llm_action",
        "config": {
            "validator": "expected_values",
            "expected_values": [
                "oui", "o", "yes", "1",
                "non", "n", "no", "2",
                "pas vraiment", "pas forcement",
            ],
            "value_map": {
                "oui": "consultation", "o": "consultation",
                "yes": "consultation", "1": "consultation",
                "non": "non_consultation", "n": "non_consultation",
                "no": "non_consultation", "2": "non_consultation",
                "pas vraiment": "non_consultation",
                "pas forcement": "non_consultation",
            },
            "context_target": "motif_visite",
        },
        "llm_prompt_success": (
            "Le patient a repondu. motif_visite = '{collected_value}'.\n"
            "Si 'consultation'     -> dis-lui simplement qu'on va l'aider et qu'on commence.\n"
            "Si 'non_consultation' -> remercie-le chaleureusement d'etre passe chez Afiya "
            "et dis-lui a bientot."
        ),
        "llm_prompt_error": (
            "Le patient a repondu '{user_input}' mais on n'a pas compris.\n"
            "Reformule la question chaleureusement : "
            "es-tu la pour une consultation ? _(oui / non)_"
        ),
        "on_success_step_id": "step-router-motif",
        "on_failure_step_id": "step-accueil",
        "is_terminal": False,
    },
    {
        "id": "step-router-motif",
        "name": "router_motif",
        "step_order": 2,
        "step_type": "condition",
        "config": {
            "left": "motif_visite",
            "operator": "==",
            "right": "consultation",
        },
        "llm_prompt_success": "",
        "llm_prompt_error": "",
        "on_success_step_id": "step-router-existant",
        "on_failure_step_id": "step-au-revoir",
        "is_terminal": False,
    },
    {
        "id": "step-au-revoir",
        "name": "au_revoir",
        "step_order": 3,
        "step_type": "llm_action",
        "config": {},
        "llm_prompt_success": (
            "Le patient n'est pas la pour une consultation.\n"
            "Genere un message chaleureux : remercie-le d'etre passe chez Afiya "
            "et dis-lui a bientot."
        ),
        "llm_prompt_error": "",
        "on_success_step_id": None,
        "on_failure_step_id": None,
        "is_terminal": True,
    },
    {
        "id": "step-router-existant",
        "name": "router_existant",
        "step_order": 4,
        "step_type": "condition",
        "config": {
            "left": "patient_existant",
            "operator": "==",
            "right": True,
        },
        "llm_prompt_success": "",
        "llm_prompt_error": "",
        "on_success_step_id": "step-accueil-existant",
        "on_failure_step_id": "step-accueil-nouveau",
        "is_terminal": False,
    },
    {
        "id": "step-accueil-existant",
        "name": "accueil_existant",
        "step_order": 5,
        "step_type": "llm_action",
        "config": {},
        "llm_prompt_success": (
            "Le patient est connu chez Afiya.\n"
            "Son prenom : {patient_prenom}. Son nom : {patient_nom}.\n"
            "Genere un message de bienvenue chaleureux et personnalise avec son prenom. "
            "Annonce qu'on va commencer par prendre ses constantes du jour."
        ),
        "llm_prompt_error": "",
        "on_success_step_id": "step-temperature",
        "on_failure_step_id": "step-accueil-existant",
        "is_terminal": False,
    },
    {
        "id": "step-accueil-nouveau",
        "name": "accueil_nouveau",
        "step_order": 6,
        "step_type": "llm_action",
        "config": {},
        "llm_prompt_success": (
            "C'est la premiere fois que ce patient vient chez Afiya.\n"
            "Genere un message chaleureux de bienvenue pour une premiere visite. "
            "Dis-lui qu'on va creer son dossier et demande-lui son *nom de famille*."
        ),
        "llm_prompt_error": "",
        "on_success_step_id": "step-nom",
        "on_failure_step_id": "step-accueil-nouveau",
        "is_terminal": False,
    },
    {
        "id": "step-nom",
        "name": "collecte_nom",
        "step_order": 7,
        "step_type": "llm_action",
        "config": {
            "validator": "nom",
            "context_target": "patient_nom",
        },
        "llm_prompt_success": "Nom valide : '{collected_value}'.\nConfirme et demande le *prenom*.",
        "llm_prompt_error": "'{user_input}' n'est pas un nom valide. Raison : {error_reason}\nRedemande le nom de famille.",
        "on_success_step_id": "step-prenom",
        "on_failure_step_id": "step-nom",
        "is_terminal": False,
    },
    {
        "id": "step-prenom",
        "name": "collecte_prenom",
        "step_order": 8,
        "step_type": "llm_action",
        "config": {
            "validator": "prenom",
            "context_target": "patient_prenom",
        },
        "llm_prompt_success": "Prenom valide : '{collected_value}'.\nPatient : {patient_nom} {collected_value}.\nConfirme chaleureusement et annonce qu'on va maintenant prendre ses constantes du jour.",
        "llm_prompt_error": "'{user_input}' n'est pas un prenom valide. Raison : {error_reason}\nRedemande le prenom.",
        "on_success_step_id": "step-temperature",
        "on_failure_step_id": "step-prenom",
        "is_terminal": False,
    },
    {
        "id": "step-temperature",
        "name": "collecte_temperature",
        "step_order": 9,
        "step_type": "llm_action",
        "config": {
            "validator": "temperature",
            "context_target": "patient_temperature",
        },
        "llm_prompt_success": "Temperature validee : {collected_value}C.\nConfirme et demande le *poids* du patient en kilogrammes.",
        "llm_prompt_error": "'{user_input}' n'est pas une temperature valide. Raison : {error_reason}\nRedemande la temperature en C (ex: 37.5).",
        "on_success_step_id": "step-poids",
        "on_failure_step_id": "step-temperature",
        "is_terminal": False,
    },
    {
        "id": "step-poids",
        "name": "collecte_poids",
        "step_order": 10,
        "step_type": "llm_action",
        "config": {
            "validator": "poids",
            "context_target": "patient_poids",
        },
        "llm_prompt_success": "Poids valide : {collected_value} kg.\nConfirme et demande la *taille* en centimetres.",
        "llm_prompt_error": "'{user_input}' n'est pas un poids valide. Raison : {error_reason}\nRedemande le poids en kg.",
        "on_success_step_id": "step-taille",
        "on_failure_step_id": "step-poids",
        "is_terminal": False,
    },
    {
        "id": "step-taille",
        "name": "collecte_taille",
        "step_order": 11,
        "step_type": "llm_action",
        "config": {
            "validator": "taille",
            "context_target": "patient_taille",
        },
        "llm_prompt_success": (
            "Taille validee : {collected_value} cm.\n"
            "Confirme et presente les specialites disponibles :\n"
            "1 Medecine Generale\n"
            "2 Cardiologie\n"
            "3 Pediatrie\n"
            "4 Dermatologie\n"
            "5 Gynecologie\n\n"
            "Demande-lui avec quel medecin il souhaite consulter aujourd'hui."
        ),
        "llm_prompt_error": "'{user_input}' n'est pas une taille valide. Raison : {error_reason}\nRedemande la taille en cm.",
        "on_success_step_id": "step-specialite",
        "on_failure_step_id": "step-taille",
        "is_terminal": False,
    },
    {
        "id": "step-specialite",
        "name": "choix_specialite",
        "step_order": 12,
        "step_type": "llm_action",
        "config": {
            "validator": "expected_values",
            "expected_values": [
                "1", "2", "3", "4", "5",
                "medecine generale", "medecine generale",
                "cardiologie",
                "pediatrie", "pediatrie",
                "dermatologie",
                "gynecologie", "gynecologie",
                "generaliste", "generaliste", "general", "general",
                "cardiologue",
                "pediatre", "pediatre",
                "dermatologue",
                "gynecologue", "gynecologue",
            ],
            "value_map": {
                "1": "GENERALISTE", "medecine generale": "GENERALISTE", "medecine generale": "GENERALISTE",
                "generaliste": "GENERALISTE", "generaliste": "GENERALISTE",
                "general": "GENERALISTE", "general": "GENERALISTE",
                "2": "CARDIOLOGUE", "cardiologie": "CARDIOLOGUE", "cardiologue": "CARDIOLOGUE",
                "3": "PEDIATRE", "pediatrie": "PEDIATRE", "pediatrie": "PEDIATRE",
                "pediatre": "PEDIATRE", "pediatre": "PEDIATRE",
                "4": "DERMATOLOGUE", "dermatologie": "DERMATOLOGUE", "dermatologue": "DERMATOLOGUE",
                "5": "GYNECOLOGUE", "gynecologie": "GYNECOLOGUE", "gynecologie": "GYNECOLOGUE",
                "gynecologue": "GYNECOLOGUE", "gynecologue": "GYNECOLOGUE",
            },
            "context_target": "patient_specialite",
        },
        "llm_prompt_success": (
            "Le patient a choisi la specialite : {collected_value}.\n"
            "Genere un message chaleureux de confirmation :\n"
            "- Remercie-le\n"
            "- Dis-lui qu'il sera mis en contact avec un {collected_value} tres prochainement\n"
            "- Souhaite-lui un bon retablissement de la part d'Afiya"
        ),
        "llm_prompt_error": (
            "Le patient a repondu '{user_input}' pour le choix de specialite.\n"
            "Raison : {error_reason}\n"
            "Reformule gentiment et reaffche les options numerotees."
        ),
        "on_success_step_id": None,
        "on_failure_step_id": "step-specialite",
        "is_terminal": True,
    },
]


def get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


def insert_workflow(table) -> None:
    pk = f"WORKFLOW#{WORKFLOW_ID}"
    sk = f"METADATA#{WORKFLOW_ID}"
    item = {
        "PK": pk,
        "SK": sk,
        "EntityType": "workflow",
        "EntityId": WORKFLOW_ID,
        "name": "Patient Collecte Afiya",
        "description": "Collecte des infos patient + orientation specialite medicale",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=item)
    print(f"  workflow: {WORKFLOW_ID}")


def insert_steps(table) -> None:
    pk = f"WORKFLOW#{WORKFLOW_ID}"
    for step in STEPS:
        step_id = step["id"]
        sk = f"STEP#{step['step_order']:03d}"

        item = {
            "PK": pk,
            "SK": sk,
            "EntityType": "workflow_step",
            "EntityId": step_id,
            "name": step["name"],
            "step_order": step["step_order"],
            "step_type": step["step_type"],
            "llm_prompt_success": step["llm_prompt_success"],
            "llm_prompt_error": step["llm_prompt_error"],
            "config": step["config"],
            "on_success_step_id": step["on_success_step_id"],
            "on_failure_step_id": step["on_failure_step_id"],
            "is_terminal": step["is_terminal"],
            "llm_model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "llm_max_tokens": 500,
            "GSI1PK": pk,
            "GSI1SK": sk,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        table.put_item(Item=item)
        print(f"  step: {step['name']} (id={step_id}, order={step['step_order']})")


def main():
    print(f"Connecting to DynamoDB table: {TABLE_NAME}")
    print(f"Region: {settings.AWS_REGION}")

    table = get_table()

    print(f"\nInserting workflow...")
    insert_workflow(table)

    print(f"\nInserting {len(STEPS)} steps...")
    insert_steps(table)

    print(f"\nDone. Workflow '{WORKFLOW_ID}' + {len(STEPS)} steps migrated to '{TABLE_NAME}'.")


if __name__ == "__main__":
    main()
