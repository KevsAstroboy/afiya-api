"""
Daily data generator — cron job to create realistic daily consultation data.
Respects: max 5 patients/day, max 5 consultations/doctor/day, max 3/doctor/15min slot.

Run:  PYTHONPATH=. python init-scripts/daily_data_generator.py
"""

import hashlib
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3
from faker import Faker

from core.config import settings

fake = Faker("fr_FR")
TABLE_NAME = "afiya-data"
DEFAULT_PASSWORD = "afiya2026"


def _hash_password(cleartext: str) -> str:
    import base64
    salt = os.urandom(16)
    data = cleartext.encode("utf-8")
    hashed = hashlib.sha256(salt + data).digest()
    return f"{base64.b64encode(hashed).decode()}.{base64.b64encode(salt).decode()}"


def _rid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decimal(v: float) -> Decimal:
    return Decimal(str(round(v, 1)))


MOTIFS = [
    "Fièvre", "Paludisme", "Hypertension", "Diabète", "Toux",
    "Douleur abdominale", "Consultation générale", "Suivi",
    "Mal de tête", "Fatigue chronique", "Infection urinaire",
    "Douleur articulaire", "Vertiges", "Insomnie", "Anémie",
]
MODES_PAIEMENT = ["Wave", "Orange Money", "MTN Money", "Espèces"]
MONTANTS = [5000, 10000, 15000, 20000]
PRENOMS_HOMMES = ["Mamadou", "Sékou", "Drissa", "Amadou", "Bakary", "Youssouf"]
PRENOMS_FEMMES = ["Aminata", "Fatoumata", "Awa", "Mariam", "Kadiatou", "Nafissatou"]
NOMS = ["Koné", "Traoré", "Ouattara", "Coulibaly", "Bamba", "Sanogo", "Cissé", "Touré"]
SYMPTOMES_PAR_MOTIF = {
    "Fièvre": ["fièvre", "courbatures", "frissons"],
    "Paludisme": ["fièvre", "maux de tête", "vomissements"],
    "Hypertension": ["vertiges", "maux de tête", "palpitations"],
    "Diabète": ["soif intense", "fatigue", "vision floue"],
    "Toux": ["toux sèche", "douleur thoracique", "essoufflement"],
    "Douleur abdominale": ["douleur au ventre", "nausées"],
    "Consultation générale": ["bilan de santé"],
    "Suivi": ["contrôle"],
    "Mal de tête": ["céphalées", "sensibilité à la lumière"],
    "Fatigue chronique": ["épuisement", "manque d'énergie"],
    "Infection urinaire": ["brûlures", "envies fréquentes"],
    "Douleur articulaire": ["genou gonflé", "raideur matinale"],
    "Vertiges": ["étourdissements", "perte d'équilibre"],
    "Insomnie": ["difficulté à dormir", "réveils nocturnes"],
    "Anémie": ["pâleur", "fatigue"],
}


def get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


def get_doctors(table) -> list:
    """Fetch doctors from DynamoDB."""
    result = table.query(
        IndexName="EntityTypeIndex",
        KeyConditionExpression="EntityType = :t",
        ExpressionAttributeValues={":t": "user"},
    )
    items = result.get("Items", [])
    return [d for d in items if d.get("type_user") == "MEDECIN"]


def get_patients(table) -> list:
    """Fetch existing patients from DynamoDB."""
    result = table.query(
        IndexName="EntityTypeIndex",
        KeyConditionExpression="EntityType = :t",
        ExpressionAttributeValues={":t": "user"},
    )
    items = result.get("Items", [])
    return [p for p in items if p.get("type_user") == "PATIENT"]


def create_patients(table, n: int) -> list:
    """Create n new patients for today."""
    password_hash = _hash_password(DEFAULT_PASSWORD)
    new_patients = []

    for _ in range(n):
        sexe = random.choice(["M", "F"])
        prenoms = PRENOMS_HOMMES if sexe == "M" else PRENOMS_FEMMES
        prenom = random.choice(prenoms)
        nom = random.choice(NOMS)
        pid = _rid("pat")
        age = random.randint(18, 65)
        birth_year = 2026 - age
        birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        operateur = random.choice(["01", "05", "07", "09"])
        telephone = f"+225{operateur}{random.randint(10000000,99999999)}"
        poids = round(random.uniform(50, 110), 1)
        taille = round(random.uniform(150, 195), 1)
        bmi = round(poids / ((taille / 100) ** 2), 1)

        item = {
            "PK": f"USER#{pid}",
            "SK": f"METADATA#{pid}",
            "EntityType": "user",
            "EntityId": pid,
            "type_user": "PATIENT",
            "telephone": telephone,
            "nom": nom.upper(),
            "prenom": prenom,
            "full_name": f"{prenom} {nom}",
            "email": f"{prenom.lower()}.{nom.lower()}@email.ci",
            "date_naissance": birth_date,
            "age": age,
            "sexe_code": sexe,
            "poids_kg": _decimal(poids),
            "taille_cm": _decimal(taille),
            "bmi": _decimal(bmi),
            "password": password_hash,
            "is_default_password": True,
            "created_at": _now(),
            "GSI1PK": "PATIENT_LIST",
            "GSI1SK": _now(),
        }
        table.put_item(Item=item)
        new_patients.append({"id": pid, "nom": nom.upper(), "prenom": prenom, "telephone": telephone})
        print(f"  + {prenom} {nom} ({pid})")

    return new_patients


def create_dossiers_medicaux(table, patients: list):
    """Create 1 dossier per new patient."""
    for p in patients:
        did = _rid("dm")
        item = {
            "PK": f"DOSSIER_MEDICAL#{did}",
            "SK": f"METADATA#{did}",
            "EntityType": "dossier_medical",
            "EntityId": did,
            "patient_id": p["id"],
            "patient_nom": p["nom"],
            "patient_prenom": p["prenom"],
            "created_at": _now(),
            "GSI1PK": f"PATIENT#{p['id']}",
            "GSI1SK": _now(),
        }
        table.put_item(Item=item)
        p["dossier_id"] = did


def today_already_seeded(table) -> bool:
    """Check if consultations exist for today."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = table.query(
        IndexName="EntityTypeIndex",
        KeyConditionExpression="EntityType = :t",
        ExpressionAttributeValues={":t": "consultation"},
    )
    for item in result.get("Items", []):
        if item.get("date_debut", "").startswith(today_str):
            return True
    return False


def distribute_consultations(table, doctors: list, patients: list, today: datetime):
    """Generate today's consultations respecting constraints."""
    weekday = today.weekday()
    n_consultations = random.randint(10, 22) if weekday < 5 else random.randint(3, 7)

    daily_doc_counts = {d["id"]: 0 for d in doctors}
    slot_counts = {}
    created = 0
    consultations = []

    slots = list(range(7 * 4, 22 * 4))  # 07h-22h × 4 slots/h

    for slot_idx in slots:
        if created >= n_consultations:
            break

        shuffled_docs = doctors[:]
        random.shuffle(shuffled_docs)

        for doc in shuffled_docs:
            if created >= n_consultations:
                break
            if daily_doc_counts[doc["id"]] >= 5:
                continue
            slot_key = (doc["id"], slot_idx)
            if slot_counts.get(slot_key, 0) >= 3:
                continue

            patient = random.choice(patients)
            cid = _rid("cons")
            motif = random.choice(MOTIFS)
            statut = random.choices(
                ["EN_COURS", "EN_ATTENTE", "TERMINEE"],
                weights=[30, 15, 55],
            )[0]
            hour = slot_idx // 4
            minute = (slot_idx % 4) * 15
            start_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=random.randint(15, 45))

            item = {
                "PK": f"CONSULTATION#{cid}",
                "SK": f"METADATA#{cid}",
                "EntityType": "consultation",
                "EntityId": cid,
                "dossier_medical_id": patient.get("dossier_id", ""),
                "patient_id": patient["id"],
                "patient_nom": patient["nom"],
                "patient_prenom": patient["prenom"],
                "patient_full_name": f"{patient['prenom']} {patient['nom']}",
                "patient_telephone": patient.get("telephone", ""),
                "medecin_id": doc["id"],
                "medecin_nom": doc.get("nom", ""),
                "medecin_prenom": doc.get("prenom", ""),
                "medecin_specialite": doc.get("specialite", ""),
                "motif": motif,
                "statut": statut,
                "date_debut": start_time.isoformat(),
                "date_cloture": end_time.isoformat() if statut == "TERMINEE" else "",
                "est_du_jour": True,
                "symptomes_rapportes": "; ".join(random.choice(SYMPTOMES_PAR_MOTIF[motif])),
                "created_at": start_time.isoformat(),
                "GSI1PK": f"PATIENT#{patient['id']}",
                "GSI1SK": start_time.isoformat(),
            }
            table.put_item(Item=item)
            consultations.append({
                "id": cid, "patient_id": patient["id"], "medecin_id": doc["id"],
                "motif": motif, "statut": statut, "date_debut": start_time,
            })

            daily_doc_counts[doc["id"]] += 1
            slot_counts[slot_key] = slot_counts.get(slot_key, 0) + 1
            created += 1

    return consultations


def seed_messages_paiements_metrics(table, consultants: list):
    """Create messages, payments and metrics for today's consultations."""
    m_count, p_count, met_count = 0, 0, 0

    with table.meta.client.get_paginator("batch_write_item") as batch:
        items = []

        for cons in consultants:
            cid = cons["id"]
            n_msgs = random.randint(5, 12)
            ts = cons["date_debut"]

            for i in range(n_msgs):
                msg_id = _rid("msg")
                is_patient = (i == 0 or i % 2 == 0)
                contenu = (
                    f"Patient: Je viens pour {cons['motif'].lower()}."
                    if is_patient
                    else f"Medecin: Je vous ecoute, decrivez vos symptomes."
                )
                ts = ts + timedelta(seconds=random.randint(5, 90))
                items.append({"PutRequest": {"Item": {
                    "PK": f"CONSULTATION#{cid}",
                    "SK": f"MSG#{ts.isoformat()}#{i:04d}",
                    "EntityType": "message", "EntityId": msg_id,
                    "consultation_id": cid,
                    "sender_type": "PATIENT" if is_patient else "MEDECIN",
                    "sender_id": cons["patient_id"] if is_patient else cons["medecin_id"],
                    "contenu": contenu, "type_contenu": "text",
                    "date_envoi": ts.isoformat(), "statut_livraison": "DELIVERED",
                }}})
                m_count += 1

            # Metrics
            for mtype, val, unite in random.sample([
                ("TEMPERATURE", round(random.uniform(36.0, 40.0), 1), "°C"),
                ("POIDS", round(random.uniform(50, 110), 1), "kg"),
                ("TAILLE", round(random.uniform(150, 195), 1), "cm"),
            ], random.randint(1, 3)):
                mid = _rid("met")
                items.append({"PutRequest": {"Item": {
                    "PK": f"CONSULTATION#{cid}",
                    "SK": f"METRIC#{mtype}#{mid}",
                    "EntityType": "metric", "EntityId": mid,
                    "consultation_id": cid,
                    "type_metric": mtype, "valeur": _decimal(val),
                    "unite": unite, "date_mesure": ts.isoformat(),
                }}})
                met_count += 1

            # Payment
            pid = _rid("pay")
            mode = random.choice(MODES_PAIEMENT)
            items.append({"PutRequest": {"Item": {
                "PK": f"PAIEMENT#{pid}", "SK": f"METADATA#{pid}",
                "EntityType": "paiement", "EntityId": pid,
                "consultation_id": cid, "patient_id": cons["patient_id"],
                "montant": _decimal(random.choice(MONTANTS)),
                "devise": "XOF", "mode_paiement": mode, "statut": "PAID",
                "transaction_id": f"TXN-{mode[:3].upper()}-{cid[-8:]}",
                "transaction_date": (ts + timedelta(minutes=5)).isoformat(),
                "GSI1PK": f"CONSULTATION#{cid}", "GSI1SK": ts.isoformat(),
            }}})
            p_count += 1

            if len(items) >= 25:
                for chunk in [items[i:i+25] for i in range(0, len(items), 25)]:
                    batch.paginate(RequestItems={TABLE_NAME: chunk})
                items = []

        if items:
            for chunk in [items[i:i+25] for i in range(0, len(items), 25)]:
                batch.paginate(RequestItems={TABLE_NAME: chunk})

    print(f"  {m_count} messages, {p_count} paiements, {met_count} metrics")


def main():
    print(f"=== Daily Data Generator: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ===\n")

    table = get_table()

    if today_already_seeded(table):
        print("Data already exists for today. Skipping.")
        return

    # Get existing doctors and patients
    doctors = get_doctors(table)
    patients = get_patients(table)
    print(f"Doctors: {len(doctors)}, Existing patients: {len(patients)}")

    # Create 2-5 new patients
    n_new_patients = random.randint(2, 5)
    print(f"\nCreating {n_new_patients} new patients...")
    new_patients = create_patients(table, n_new_patients)
    create_dossiers_medicaux(table, new_patients)
    all_patients = patients + new_patients

    if not all_patients:
        print("No patients available. Seed the database first.")
        return

    # Distribute consultations
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"\nDistributing consultations for {today.strftime('%Y-%m-%d')}...")
    consultants = distribute_consultations(table, doctors, all_patients, today)
    print(f"  {len(consultants)} consultations created")

    # Per-doctor stats
    print("\nDoctor workload today:")
    for doc in doctors:
        count = sum(1 for c in consultants if c["medecin_id"] == doc["id"])
        print(f"  Dr {doc.get('prenom','')} {doc.get('nom','')}: {count} consultations")

    # Messages + payments + metrics
    print(f"\nGenerating messages, payments, metrics...")
    seed_messages_paiements_metrics(table, consultants)

    print(f"\n=== Daily generation complete ===")


if __name__ == "__main__":
    main()
