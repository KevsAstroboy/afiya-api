"""
Seed script: Generate realistic Ivorian medical data into DynamoDB afiya-data.

Run:  PYTHONPATH=. python init-scripts/seed_dynamodb.py
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

# ── Password hashing (same as Utilities.encrypt_password) ──
def _hash_password(cleartext: str) -> str:
    import base64
    salt = os.urandom(16)
    data = cleartext.encode("utf-8")
    hashed = hashlib.sha256(salt + data).digest()
    return f"{base64.b64encode(hashed).decode()}.{base64.b64encode(salt).decode()}"


# ── Helpers ──
def _rid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decimal(v: float) -> Decimal:
    return Decimal(str(round(v, 1)))


def _random_time_on_day(day: datetime, start_hour: int = 7, end_hour: int = 22) -> datetime:
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ── Data pools ──
MOTIFS = [
    "Fièvre", "Paludisme", "Hypertension", "Diabète", "Toux",
    "Douleur abdominale", "Consultation générale", "Suivi",
    "Mal de tête", "Fatigue chronique", "Infection urinaire",
    "Douleur articulaire", "Vertiges", "Insomnie", "Anémie",
]

MODES_PAIEMENT = ["Wave", "Orange Money", "MTN Money", "Espèces"]
MONTANTS = [5000, 10000, 15000, 20000]
CLINIQUES = ["CHU Cocody", "CHU Treichville", "CHU Yopougon", "Clinique Angré", "Clinique Plateau"]

PRENOMS_HOMMES = [
    "Mamadou", "Sékou", "Drissa", "Amadou", "Bakary", "Youssouf", "Moussa",
    "Issa", "Lassina", "Siaka", "Adama", "Karim", "Brahima", "Oumar", "Fodé",
]
PRENOMS_FEMMES = [
    "Aminata", "Fatoumata", "Awa", "Mariam", "Kadiatou", "Nafissatou",
    "Aïssata", "Saran", "Bintou", "Fanta", "Salimata", "Adjaratou", "Nahawa",
    "Maimouna", "Djeneba",
]
NOMS = [
    "Koné", "Traoré", "Ouattara", "Coulibaly", "Bamba", "Sanogo", "Cissé",
    "Touré", "Diarra", "Konaté", "Doumbia", "Sidibé", "Sylla", "Berthé",
    "Dembélé", "Samaké", "Sangaré", "Fofana",
]

DOCTORS = [
    {"id": "med_a1b2c3d4", "nom": "Traoré", "prenom": "Drissa", "specialite": "GENERALISTE", "tel": "+2250701020304"},
    {"id": "med_b2c3d4e5", "nom": "Koné", "prenom": "Fatoumata", "specialite": "CARDIOLOGUE", "tel": "+2250502030405"},
    {"id": "med_c3d4e5f6", "nom": "Ouattara", "prenom": "Mamadou", "specialite": "PEDIATRE", "tel": "+2250103040506"},
    {"id": "med_d4e5f6a7", "nom": "Bamba", "prenom": "Awa", "specialite": "DERMATOLOGUE", "tel": "+2250704050607"},
    {"id": "med_e5f6a7b8", "nom": "Coulibaly", "prenom": "Sékou", "specialite": "GYNECOLOGUE", "tel": "+2250905060708"},
]

SYMPTOMES_PAR_MOTIF = {
    "Fièvre": ["fièvre", "courbatures", "frissons"],
    "Paludisme": ["fièvre", "maux de tête", "vomissements"],
    "Hypertension": ["vertiges", "maux de tête", "palpitations"],
    "Diabète": ["soif intense", "fatigue", "vision floue"],
    "Toux": ["toux sèche", "douleur thoracique", "essoufflement"],
    "Douleur abdominale": ["douleur au ventre", "nausées", "perte d'appétit"],
    "Consultation générale": ["bilan de santé", "pas de symptôme particulier"],
    "Suivi": ["contrôle", "pas de nouveau symptôme"],
    "Mal de tête": ["céphalées", "sensibilité à la lumière", "nausées"],
    "Fatigue chronique": ["épuisement", "manque d'énergie", "sommeil non réparateur"],
    "Infection urinaire": ["brûlures", "envies fréquentes", "douleur pelvienne"],
    "Douleur articulaire": ["genou gonflé", "raideur matinale", "difficulté à marcher"],
    "Vertiges": ["étourdissements", "perte d'équilibre", "nausées"],
    "Insomnie": ["difficulté à dormir", "réveils nocturnes", "anxiété"],
    "Anémie": ["pâleur", "fatigue", "essoufflement"],
}

MESSAGE_TEMPLATES_PATIENT = [
    "Bonjour docteur, je ne me sens pas bien depuis quelques jours.",
    "Docteur, j'ai {symptome} depuis {jours} jours.",
    "Bonjour, je viens pour une consultation. J'ai {symptome}.",
    "Docteur j'ai mal, {symptome} ne passe pas.",
    "Je tousse beaucoup et j'ai de la fièvre, pouvez-vous m'aider ?",
    "Depuis {jours} jours j'ai {symptome}, ça m'inquiète.",
    "Bonjour, je suis là pour mon rendez-vous de suivi.",
    "Docteur, {symptome} empire malgré les médicaments.",
    "Je viens consulter pour {symptome}, merci de me recevoir.",
    "Bonjour, j'aimerais faire un bilan de santé général.",
]

MESSAGE_TEMPLATES_MEDECIN = [
    "Bonjour, je vous écoute. Décrivez-moi vos symptômes.",
    "Depuis combien de temps avez-vous ces symptômes ?",
    "Avez-vous pris des médicaments récemment ?",
    "Je vais vous examiner. Avez-vous de la fièvre ?",
    "D'accord, je vous prescris un traitement. Prenez-le {fois} fois par jour.",
    "Je vous recommande de faire des examens complémentaires.",
    "Votre tension est un peu élevée. Surveillez votre alimentation.",
    "Le traitement dure {duree} jours. Revenez me voir si ça ne s'améliore pas.",
    "Voici votre ordonnance. À la pharmacie du quartier.",
    "Prenez rendez-vous dans {suivi} jours pour le contrôle.",
]

DIAGNOSTICS = [
    "Paludisme simple", "Hypertension artérielle légère", "Diabète de type 2",
    "Infection respiratoire", "Gastrite", "Anémie ferriprive", "Lombalgie",
    "Céphalée de tension", "Insomnie primaire", "Rhinite allergique",
    "Dermatite atopique", "Infection urinaire basse",
]

TRAITEMENTS = [
    "Artéméther 80mg + Luméfantrine 480mg, 2x/jour, 3 jours",
    "Amlodipine 5mg, 1x/jour, 30 jours",
    "Metformine 500mg, 2x/jour, 30 jours",
    "Amoxicilline 500mg, 3x/jour, 7 jours",
    "Oméprazole 20mg, 1x/jour, 14 jours",
    "Fer + Acide folique, 1x/jour, 30 jours",
    "Ibuprofène 400mg, 2x/jour, 5 jours",
    "Paracétamol 500mg, si douleur, max 3x/jour",
    "Mélatonine 2mg, 1x/jour au coucher, 15 jours",
    "Cétirizine 10mg, 1x/jour, 10 jours",
    "Crème hydrocortisone 1%, 2x/jour, 7 jours",
    "Fosfomycine 3g, dose unique",
]


def get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


# ═══════════════════════════════════════════════════════════
# PHASE 1: Doctors (5)
# ═══════════════════════════════════════════════════════════
def seed_doctors(table) -> list:
    doctors = []
    password_hash = _hash_password(DEFAULT_PASSWORD)
    for d in DOCTORS:
        item = {
            "PK": f"USER#{d['id']}",
            "SK": f"METADATA#{d['id']}",
            "EntityType": "user",
            "EntityId": d["id"],
            "type_user": "MEDECIN",
            "telephone": d["tel"],
            "nom": d["nom"].upper(),
            "prenom": d["prenom"],
            "full_name": f"Dr {d['prenom']} {d['nom']}",
            "email": f"dr.{d['nom'].lower()}@afiya.ci",
            "sexe_code": "M" if d["prenom"] in ["Drissa", "Mamadou", "Sékou"] else "F",
            "specialite": d["specialite"],
            "statut_code": "ACTIF",
            "password": password_hash,
            "is_default_password": True,
            "disponible": True,
            "created_at": "2026-01-01T00:00:00Z",
            "GSI1PK": "MEDECIN_LIST",
            "GSI1SK": d["specialite"],
        }
        table.put_item(Item=item)
        doctors.append(d)
        print(f"  Dr {d['prenom']} {d['nom']} ({d['specialite']})")

    return doctors


# ═══════════════════════════════════════════════════════════
# PHASE 2: Patients (50)
# ═══════════════════════════════════════════════════════════
def seed_patients(table, n=50) -> list:
    patients = []
    password_hash = _hash_password(DEFAULT_PASSWORD)

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
        numero = f"{random.randint(10000000,99999999)}"
        telephone = f"+225{operateur}{numero}"
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
            "lieu_naissance": "Abidjan",
            "sexe_code": sexe,
            "sexe": "FEMININ" if sexe == "F" else "MASCULIN",
            "statut_code": "ACTIF",
            "statut": "ACTIF",
            "clinique": random.choice(CLINIQUES),
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
        patients.append({"id": pid, "nom": nom.upper(), "prenom": prenom, "telephone": telephone})
        print(f"  {prenom} {nom} ({pid})")

    return patients


# ═══════════════════════════════════════════════════════════
# PHASE 3: Dossiers Médicaux (1 par patient)
# ═══════════════════════════════════════════════════════════
def seed_dossiers_medicaux(table, patients: list) -> list:
    dossiers = []
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
        dossiers.append({"id": did, "patient_id": p["id"]})
    print(f"  {len(dossiers)} dossiers medicaux crees")
    return dossiers


# ═══════════════════════════════════════════════════════════
# PHASE 4: Consultations (200 sur 30 jours)
# ═══════════════════════════════════════════════════════════
def _distribute_consultations(table, doctors: list, dossiers: list, patients: list, total_days: int = 30):
    """Distribute consultations respecting max 5/doctor/day and max 3/doctor/15min slot."""
    today = datetime.now(timezone.utc)
    consultations = []

    print(f"  DEBUG: doctors={len(doctors)}, dossiers={len(dossiers)}, patients={len(patients)}, total_days={total_days}")

    # Precompute a target per day respecting weekday/weekend ratio
    daily_targets = []
    for d in range(total_days):
        day = today - timedelta(days=total_days - d)
        weekday = day.weekday()
        if weekday < 5:  # weekday
            target = random.randint(6, 10)  # higher volume
        else:
            target = random.randint(3, 5)  # weekend lower
        daily_targets.append((day, target))

    daily_counts = {doc["id"]: 0 for doc in doctors}

    for day, target in daily_targets:
        created_today = 0
        slot_15min_counts = {}  # (doc_id, slot_min) -> count
        daily_doc_counts = {doc["id"]: 0 for doc in doctors}

        slots = list(range(7 * 4, 22 * 4))  # 07h00-22h00 en slots de 15min

        for slot_idx in slots:
            if created_today >= target:
                break

            shuffled_docs = doctors[:]
            random.shuffle(shuffled_docs)

            for doc in shuffled_docs:
                if created_today >= target:
                    break
                if daily_doc_counts[doc["id"]] >= 5:
                    continue
                slot_key = (doc["id"], slot_idx)
                if slot_15min_counts.get(slot_key, 0) >= 3:
                    continue

                # Create consultation
                dossier = random.choice(dossiers)
                try:
                    patient = next(p for p in patients if p["id"] == dossier["patient_id"])
                except StopIteration:
                    print(f"    WARN: no patient found for dossier {dossier['id']}, patient_id={dossier['patient_id']}, available patients={[p['id'] for p in patients[:5]]}...")
                    continue
                cid = _rid("cons")
                motif = random.choice(MOTIFS)
                statut = random.choices(
                    ["EN_COURS", "EN_ATTENTE", "TERMINEE", "ANNULEE"],
                    weights=[20, 10, 60, 10],
                )[0]
                start_time = _random_time_on_day(day, slot_idx // 4, min(slot_idx // 4 + 1, 22))
                end_time = start_time + timedelta(minutes=random.randint(15, 45)) if statut == "TERMINEE" else start_time

                item = {
                    "PK": f"CONSULTATION#{cid}",
                    "SK": f"METADATA#{cid}",
                    "EntityType": "consultation",
                    "EntityId": cid,
                    "dossier_medical_id": dossier["id"],
                    "patient_id": patient["id"],
                    "patient_nom": patient["nom"],
                    "patient_prenom": patient["prenom"],
                    "patient_full_name": f"{patient['prenom']} {patient['nom']}",
                    "patient_telephone": patient["telephone"],
                    "medecin_id": doc["id"],
                    "medecin_nom": doc["nom"],
                    "medecin_prenom": doc["prenom"],
                    "medecin_specialite": doc["specialite"],
                    "motif": motif,
                    "statut": statut,
                    "date_debut": start_time.isoformat(),
                    "date_cloture": end_time.isoformat() if statut == "TERMINEE" else "",
                    "est_du_jour": day.date() == today.date(),
                    "symptomes_rapportes": "; ".join(random.choice(SYMPTOMES_PAR_MOTIF[motif])),
                    "created_at": start_time.isoformat(),
                    "GSI1PK": f"PATIENT#{patient['id']}",
                    "GSI1SK": start_time.isoformat(),
                }
                table.put_item(Item=item)
                consultations.append({
                    "id": cid, "patient_id": patient["id"], "medecin_id": doc["id"],
                    "motif": motif, "statut": statut, "date_debut": start_time,
                    "dossier_id": dossier["id"],
                })

                daily_doc_counts[doc["id"]] += 1
                slot_15min_counts[slot_key] = slot_15min_counts.get(slot_key, 0) + 1
                created_today += 1

        if created_today > 0:
            print(f"    {day.strftime('%Y-%m-%d')}: {created_today} consultations")

    print(f"  {len(consultations)} consultations creees")
    return consultations


# ═══════════════════════════════════════════════════════════
# PHASE 5: Messages + Paiements + Metrics + Avis
# ═══════════════════════════════════════════════════════════
def seed_messages_paiements_metrics_avis(table, consultants: list):
    messages_count = 0
    paiements_count = 0
    metrics_count = 0
    avis_count = 0

    for cons in consultants:
        cid = cons["id"]
        n_msgs = random.randint(5, 15)
        ts = cons["date_debut"]

        # Messages
        for i in range(n_msgs):
            msg_id = _rid("msg")
            is_patient = (i == 0 or random.random() < 0.5)
            if is_patient:
                template = random.choice(MESSAGE_TEMPLATES_PATIENT)
                contenu = template.format(
                    symptome=random.choice(SYMPTOMES_PAR_MOTIF.get(cons["motif"], ["symptôme"])),
                    jours=random.randint(2, 10),
                )
            else:
                template = random.choice(MESSAGE_TEMPLATES_MEDECIN)
                contenu = template.format(
                    fois=random.randint(1, 3),
                    duree=random.choice([3, 5, 7, 10, 14]),
                    suivi=random.choice([7, 14, 30]),
                )

            ts = ts + timedelta(seconds=random.randint(5, 120))

            table.put_item(Item={
                "PK": f"CONSULTATION#{cid}",
                "SK": f"MSG#{ts.isoformat()}#{i:04d}",
                "EntityType": "message",
                "EntityId": msg_id,
                "consultation_id": cid,
                "sender_type": "PATIENT" if is_patient else "MEDECIN",
                "sender_id": cons["patient_id"] if is_patient else cons["medecin_id"],
                "contenu": contenu,
                "type_contenu": "text",
                "date_envoi": ts.isoformat(),
                "statut_livraison": "DELIVERED",
            })
            messages_count += 1

        # Metrics (2-5 per consultation)
        metric_types = random.sample(
            ["TEMPERATURE", "POIDS", "TAILLE", "TENSION_SYSTOLIQUE", "TENSION_DIASTOLIQUE"],
            random.randint(2, 5),
        )
        for mtype in metric_types:
            mid = _rid("met")
            val = {
                "TEMPERATURE": round(random.uniform(36.0, 41.0), 1),
                "POIDS": round(random.uniform(50, 110), 1),
                "TAILLE": round(random.uniform(150, 195), 1),
                "TENSION_SYSTOLIQUE": round(random.uniform(110, 180), 0),
                "TENSION_DIASTOLIQUE": round(random.uniform(60, 110), 0),
            }.get(mtype, 0)
            unite = {"TEMPERATURE": "°C", "POIDS": "kg", "TAILLE": "cm",
                     "TENSION_SYSTOLIQUE": "mmHg", "TENSION_DIASTOLIQUE": "mmHg"}.get(mtype, "")

            table.put_item(Item={
                "PK": f"CONSULTATION#{cid}",
                "SK": f"METRIC#{mtype}#{mid}",
                "EntityType": "metric",
                "EntityId": mid,
                "consultation_id": cid,
                "type_metric": mtype,
                "valeur": _decimal(val),
                "unite": unite,
                "date_mesure": ts.isoformat(),
            })
            metrics_count += 1

        # Payment
        if cons["statut"] in ("TERMINEE", "EN_COURS"):
            pid = _rid("pay")
            mode = random.choice(MODES_PAIEMENT)
            montant = random.choice(MONTANTS)
            table.put_item(Item={
                "PK": f"PAIEMENT#{pid}",
                "SK": f"METADATA#{pid}",
                "EntityType": "paiement",
                "EntityId": pid,
                "consultation_id": cid,
                "patient_id": cons["patient_id"],
                "medecin_id": cons["medecin_id"],
                "montant": _decimal(montant),
                "devise": "XOF",
                "mode_paiement": mode,
                "statut": "PAID",
                "transaction_id": f"TXN-{mode[:3].upper()}-{cid[-8:]}",
                "transaction_date": (ts + timedelta(minutes=5)).isoformat(),
                "GSI1PK": f"CONSULTATION#{cid}",
                "GSI1SK": ts.isoformat(),
            })
            paiements_count += 1

        # Avis
        if cons["statut"] in ("TERMINEE", "EN_COURS") and random.random() < 0.7:
            aid = _rid("avis")
            note = random.randint(2, 5)
            commentaires = [
                "Très bon accueil, médecin à l'écoute.",
                "Consultation rapide et efficace.",
                "Bon diagnostic, traitement adapté.",
                "Je recommande ce médecin.",
                "Rendez-vous respecté, service professionnel.",
            ]
            table.put_item(Item={
                "PK": f"CONSULTATION#{cid}",
                "SK": f"AVIS#{aid}",
                "EntityType": "avis_consultation",
                "EntityId": aid,
                "consultation_id": cid,
                "note": note,
                "commentaire": random.choice(commentaires),
                "created_at": (ts + timedelta(hours=1)).isoformat(),
            })
            avis_count += 1

    print(f"  {messages_count} messages")
    print(f"  {paiements_count} paiements")
    print(f"  {metrics_count} metrics")
    print(f"  {avis_count} avis")


# ═══════════════════════════════════════════════════════════
# PHASE 6: Résumés IA (pre-generated, no Bedrock call)
# ═══════════════════════════════════════════════════════════
def seed_resumes_ia(table, consultants: list):
    count = 0
    for cons in consultants:
        rid = _rid("ria")
        motif = cons["motif"]
        symptomes = SYMPTOMES_PAR_MOTIF.get(motif, [motif])

        niveau = random.choices(
            ["FAIBLE", "MODERE", "ELEVE", "CRITIQUE"],
            weights=[30, 45, 20, 5],
        )[0]

        facteurs = random.sample(
            ["Voyage récent en zone endémique", "Antécédents familiaux",
             "Stress chronique", "Sédentarité", "Alimentation déséquilibrée",
             "Tabagisme", "Consommation d'alcool"],
            random.randint(0, 3),
        )

        recommandations = {
            "FAIBLE": "Repos et surveillance à domicile. Consulter si aggravation.",
            "MODERE": "Consultation de suivi recommandée dans 7 jours.",
            "ELEVE": "Examens complémentaires urgents. Suivi rapproché nécessaire.",
            "CRITIQUE": "Orientation vers un spécialiste en urgence.",
        }[niveau]

        item = {
            "PK": f"RESUME_IA#{rid}",
            "SK": f"METADATA#{rid}",
            "EntityType": "resume_ia",
            "EntityId": rid,
            "consultation_id": cons["id"],
            "symptomes": symptomes,
            "facteurs_risque": facteurs,
            "niveau_risque": niveau,
            "recommandation": recommandations,
            "generated_at": _now(),
            "GSI1PK": f"CONSULTATION#{cons['id']}",
            "GSI1SK": _now(),
        }
        table.put_item(Item=item)
        count += 1

    print(f"  {count} resumes IA generes")


def main():
    print(f"=== Seed DynamoDB: {TABLE_NAME} ===\n")

    table = get_table()

    print("PHASE 1: Medecins (5)")
    doctors = seed_doctors(table)

    print("\nPHASE 2: Patients (50)")
    patients = seed_patients(table, 50)

    print("\nPHASE 3: Dossiers medicaux")
    dossiers = seed_dossiers_medicaux(table, patients)

    print("\nPHASE 4: Consultations (~200 sur 30 jours)")
    consultants = _distribute_consultations(table, doctors, dossiers, patients)

    print("\nPHASE 5: Messages + Paiements + Metrics + Avis")
    seed_messages_paiements_metrics_avis(table, consultants)

    print("\nPHASE 6: Resumes IA")
    seed_resumes_ia(table, consultants)

    print(f"\n=== Seed termine ===")


if __name__ == "__main__":
    main()
