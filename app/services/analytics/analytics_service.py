"""
Analytics service — queries DynamoDB afiya-data for KPIs and aggregations.
Flexible date range + period (day/week/month/year).
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

import base64
import json

import boto3

from core.config import settings

TABLE_NAME = "afiya-data"


def _get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


def _scan(entity_type: str) -> list:
    table = _get_table()
    items = []
    last_key = None
    while True:
        kwargs = {
            "IndexName": "EntityTypeIndex",
            "KeyConditionExpression": "EntityType = :t",
            "ExpressionAttributeValues": {":t": entity_type},
        }
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        result = table.query(**kwargs)
        items.extend(result.get("Items", []))
        last_key = result.get("LastEvaluatedKey")
        if not last_key:
            break
    return items


def _encode_key(key: dict) -> str:
    return base64.b64encode(json.dumps(key).encode()).decode()


def _decode_key(token: str) -> dict:
    return json.loads(base64.b64decode(token.encode()))


def _period_key(date: datetime, period: str) -> str:
    if period == "day":
        return date.strftime("%Y-%m-%d")
    elif period == "week":
        iso = date.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    elif period == "month":
        return date.strftime("%Y-%m")
    elif period == "year":
        return date.strftime("%Y")
    return date.strftime("%Y-%m-%d")


def _period_range(date_start: datetime, date_end: datetime, period: str) -> list:
    """Return (label, start, end) tuples for each period in range."""
    ranges = []
    current = date_start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = date_end.replace(hour=23, minute=59, second=59)

    while current <= end:
        if period == "day":
            next_cut = current + timedelta(days=1)
            label = current.strftime("%Y-%m-%d")
        elif period == "week":
            next_cut = current + timedelta(days=7 - current.weekday())
            label = _period_key(current, "week")
        elif period == "month":
            if current.month == 12:
                next_cut = current.replace(year=current.year + 1, month=1, day=1)
            else:
                next_cut = current.replace(month=current.month + 1, day=1)
            label = current.strftime("%Y-%m")
        elif period == "year":
            next_cut = current.replace(year=current.year + 1, month=1, day=1)
            label = current.strftime("%Y")
        else:
            next_cut = current + timedelta(days=1)
            label = current.strftime("%Y-%m-%d")

        ranges.append({
            "period_key": label,
            "start": current.isoformat(),
            "end": (min(next_cut - timedelta(seconds=1), end)).isoformat(),
        })
        current = next_cut

    return ranges


def _in_range(date_str: str, start_str: str, end_str: str) -> bool:
    if not date_str:
        return False
    try:
        d = date_str[:19]  # "2026-06-28T09:15:00"
    except (IndexError, TypeError):
        return False
    return start_str[:10] <= d[:10] <= end_str[:10]


def _safe_int(v) -> int:
    try:
        return int(Decimal(str(v)))
    except (ValueError, TypeError, InvalidOperation):
        return 0


def _safe_decimal(v) -> Decimal:
    try:
        return Decimal(str(v))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal("0")


def get_analytics(
    date_debut: str,
    date_fin: str,
    period: str = "day",
) -> dict:
    """
    Main analytics endpoint — flexible date range + period.

    Returns:
        {
          "period": "day",
          "date_debut": "2026-06-01",
          "date_fin": "2026-06-30",
          "resume": { total_consultations, total_patients, total_revenue_xof, ... },
          "series": [{ period_key, consultations, terminees, revenue_xof, ... }],
          "top_motifs": [{ motif, count }],
          "stats_medecins": [{ medecin_id, nom, consultations, revenue }],
          "patients_aujourdhui": [...]  # only if range covers today
        }
    """
    try:
        date_start = datetime.strptime(date_debut, "%Y-%m-%d")
        date_end = datetime.strptime(date_fin, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except (ValueError, TypeError):
        today = datetime.now(timezone.utc)
        date_start = today.replace(hour=0, minute=0, second=0)
        date_end = today.replace(hour=23, minute=59, second=59)
        date_debut = date_start.strftime("%Y-%m-%d")
        date_fin = date_end.strftime("%Y-%m-%d")

    # Fetch all consultations and payments in range
    consultations = _scan("consultation")
    paiements = _scan("paiement")
    users = _scan("user")
    patients_list = [u for u in users if u.get("type_user") == "PATIENT"]
    doctors_list = [u for u in users if u.get("type_user") == "MEDECIN"]

    periods = _period_range(date_start, date_end, period)

    # Init series buckets
    series_buckets = defaultdict(lambda: {
        "consultations": 0, "en_attente": 0, "terminees": 0, "annulees": 0,
        "revenue_xof": 0, "nouveaux_patients": 0,
    })

    motif_counts = defaultdict(int)
    doctor_stats = defaultdict(lambda: {"consultations": 0, "revenue_xof": 0})
    patients_today = []

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    covers_today = date_start.strftime("%Y-%m-%d") <= today_str <= date_end.strftime("%Y-%m-%d")

    # Aggregate consultations
    for item in consultations:
        date_debut_item = item.get("date_debut", "")
        if not date_debut_item:
            continue

        item_date = datetime.fromisoformat(date_debut_item[:19].replace("Z", "+00:00"))
        if item_date < date_start or item_date > date_end:
            continue

        pk = _period_key(item_date, period)
        series_buckets[pk]["consultations"] += 1

        statut = item.get("statut", "")
        if statut == "EN_ATTENTE":
            series_buckets[pk]["en_attente"] += 1
        elif statut == "TERMINEE":
            series_buckets[pk]["terminees"] += 1
        elif statut == "ANNULEE":
            series_buckets[pk]["annulees"] += 1

        motif = item.get("motif", "")
        if motif:
            motif_counts[motif] += 1

        medecin_id = item.get("medecin_id", "")
        if medecin_id:
            doctor_stats[medecin_id]["consultations"] += 1

        # Patients today
        if covers_today and date_debut_item[:10] == today_str:
            patients_today.append({
                "nom": item.get("patient_nom", ""),
                "prenom": item.get("patient_prenom", ""),
                "heure": date_debut_item[11:16],
                "motif": motif,
                "statut": statut,
                "consultation_id": item.get("EntityId", ""),
            })

    # Aggregate payments for revenue
    for item in paiements:
        tx_date = item.get("transaction_date", "")
        if not tx_date:
            continue
        try:
            tx_dt = datetime.fromisoformat(tx_date[:19].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if tx_dt < date_start or tx_dt > date_end:
            continue

        pk = _period_key(tx_dt, period)
        montant = _safe_int(item.get("montant", 0))
        series_buckets[pk]["revenue_xof"] += montant

        medecin_id = item.get("medecin_id", "")
        if medecin_id:
            doctor_stats[medecin_id]["revenue_xof"] += montant

    # Build series output
    series = []
    for p in periods:
        pk = p["period_key"]
        b = series_buckets.get(pk, {
            "consultations": 0, "en_attente": 0, "terminees": 0,
            "annulees": 0, "revenue_xof": 0, "nouveaux_patients": 0,
        })
        series.append({
            "period_start": p["start"][:10],
            "period_end": p["end"][:10],
            **b,
        })

    # Top motifs
    top_motifs = sorted(
        [{"motif": k, "count": v} for k, v in motif_counts.items()],
        key=lambda x: x["count"], reverse=True,
    )[:5]

    # Doctor stats
    doctor_lookup = {d.get("EntityId", ""): d for d in doctors_list}
    stats_medecins = []
    for med_id, stats in sorted(doctor_stats.items()):
        doc = doctor_lookup.get(med_id, {})
        stats_medecins.append({
            "medecin_id": med_id,
            "medecin_nom": f"Dr {doc.get('prenom','')} {doc.get('nom','')}",
            "specialite": doc.get("specialite", ""),
            "consultations": stats["consultations"],
            "revenue_xof": stats["revenue_xof"],
            "taux_occupation": f"{min(100, stats['consultations'] * 100 // 5)}%",
        })

    # Resume
    total_c = sum(s["consultations"] for s in series)
    total_r = sum(s["revenue_xof"] for s in series)
    patient_ids = set()
    for item in consultations:
        pid = item.get("patient_id")
        if pid:
            patient_ids.add(pid)

    resume = {
        "total_consultations": total_c,
        "total_patients": len(patient_ids),
        "total_revenue_xof": total_r,
    }

    result = {
        "period": period,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "resume": resume,
        "series": series,
        "top_motifs": top_motifs,
        "stats_medecins": stats_medecins,
    }

    if covers_today:
        result["patients_aujourdhui"] = patients_today

    return result


def get_patient_with_history(patient_id: str) -> Optional[dict]:
    """Get patient info + list of consultation summaries."""
    table = _get_table()
    result = table.get_item(Key={"PK": f"USER#{patient_id}", "SK": f"METADATA#{patient_id}"})
    patient = result.get("Item")
    if not patient:
        return None

    # Query consultations by patient
    consultations = []
    result = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": f"PATIENT#{patient_id}"},
        ScanIndexForward=False,
    )
    for item in result.get("Items", []):
        if item.get("EntityType") == "consultation":
            consultations.append({
                "consultation_id": item.get("EntityId"),
                "date": item.get("date_debut", "")[:10],
                "motif": item.get("motif", ""),
                "medecin_nom": item.get("medecin_nom", ""),
                "medecin_prenom": item.get("medecin_prenom", ""),
                "statut": item.get("statut", ""),
            })

    return {
        "patient": {
            "id": patient.get("EntityId"),
            "nom": patient.get("nom"),
            "prenom": patient.get("prenom"),
            "telephone": patient.get("telephone"),
            "date_naissance": patient.get("date_naissance"),
            "age": patient.get("age"),
            "sexe": patient.get("sexe_code"),
            "poids_kg": patient.get("poids_kg"),
            "taille_cm": patient.get("taille_cm"),
            "bmi": patient.get("bmi"),
            "clinique": patient.get("clinique"),
        },
        "consultations": consultations,
    }


def get_consultation_detail(consultation_id: str) -> Optional[dict]:
    """Full consultation fiche: patient, consultation, paiement, messages, resume, metriques, avis."""
    table = _get_table()
    pk = f"CONSULTATION#{consultation_id}"

    # Get consultation
    result = table.get_item(Key={"PK": pk, "SK": f"METADATA#{consultation_id}"})
    cons = result.get("Item")
    if not cons:
        return None

    # Get patient
    patient_id = cons.get("patient_id")
    patient_info = None
    if patient_id:
        pr = table.get_item(Key={"PK": f"USER#{patient_id}", "SK": f"METADATA#{patient_id}"})
        p = pr.get("Item")
        if p:
            patient_info = {
                "id": p.get("EntityId"),
                "nom": p.get("nom"),
                "prenom": p.get("prenom"),
                "full_name": p.get("full_name"),
                "telephone": p.get("telephone"),
                "date_naissance": p.get("date_naissance"),
                "age": p.get("age"),
                "sexe": p.get("sexe", p.get("sexe_code")),
                "poids_kg": p.get("poids_kg"),
                "taille_cm": p.get("taille_cm"),
                "bmi": p.get("bmi"),
                "clinique": p.get("clinique"),
            }

    # Get messages
    messages = []
    msg_result = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": pk, ":sk": "MSG#"},
    )
    for m in msg_result.get("Items", []):
        messages.append({
            "sender_type": m.get("sender_type"),
            "sender_id": m.get("sender_id"),
            "contenu": m.get("contenu"),
            "date": m.get("date_envoi", ""),
            "type_contenu": m.get("type_contenu", "text"),
        })

    # Get paiement
    paiement_info = None
    pay_result = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": pk},
    )
    for item in pay_result.get("Items", []):
        if item.get("EntityType") == "paiement":
            paiement_info = {
                "mode": item.get("mode_paiement"),
                "montant": item.get("montant"),
                "devise": item.get("devise", "XOF"),
                "statut": item.get("statut"),
                "date": item.get("transaction_date", ""),
            }
            break

    # Get resume IA
    resume_ia_info = None
    # Query RESUME_IA items with GSI1PK = CONSULTATION#id
    ria_result = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": pk},
    )
    for item in ria_result.get("Items", []):
        if item.get("EntityType") == "resume_ia":
            resume_ia_info = {
                "symptomes": item.get("symptomes", []),
                "facteurs_risque": item.get("facteurs_risque", []),
                "niveau_risque": item.get("niveau_risque"),
                "recommandation": item.get("recommandation"),
                "resume": item.get("resume"),
            }
            break

    # Get metriques
    metriques = []
    met_result = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": pk, ":sk": "METRIC#"},
    )
    for m in met_result.get("Items", []):
        metriques.append({
            "type": m.get("type_metric"),
            "valeur": m.get("valeur"),
            "unite": m.get("unite"),
            "date": m.get("date_mesure", ""),
        })

    # Get avis
    avis_info = None
    avis_result = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": pk, ":sk": "AVIS#"},
    )
    for a in avis_result.get("Items", []):
        avis_info = {
            "note": a.get("note"),
            "commentaire": a.get("commentaire"),
            "date": a.get("created_at", ""),
        }
        break

    return {
        "patient": patient_info,
        "consultation": {
            "id": cons.get("EntityId"),
            "dossier_medical_id": cons.get("dossier_medical_id"),
            "medecin_nom": cons.get("medecin_nom"),
            "medecin_prenom": cons.get("medecin_prenom"),
            "medecin_specialite": cons.get("medecin_specialite"),
            "motif": cons.get("motif"),
            "statut": cons.get("statut"),
            "date_debut": cons.get("date_debut"),
            "date_cloture": cons.get("date_cloture", ""),
            "symptomes_rapportes": cons.get("symptomes_rapportes"),
        },
        "paiement": paiement_info,
        "messages": messages,
        "resume_ia": resume_ia_info,
        "metriques": metriques,
        "avis": avis_info,
    }


def get_consultations(
    limit: int = 20,
    start_key: Optional[str] = None,
    statut: Optional[str] = None,
    date: Optional[str] = None,
    medecin_id: Optional[str] = None,
    patient_id: Optional[str] = None,
) -> dict:
    """List consultations paginated with optional filters.

    DynamoDB FilterExpression is applied AFTER Limit, so a single query may
    return fewer than `limit` items even if more exist. We accumulate items
    across pages until we reach `limit` or exhaust all pages.
    """
    table = _get_table()

    expr_values = {":t": "consultation"}
    filter_parts = []

    if statut:
        expr_values[":s"] = statut
        filter_parts.append("statut = :s")
    if date:
        expr_values[":d"] = date
        filter_parts.append("begins_with(date_debut, :d)")
    if medecin_id:
        expr_values[":m"] = medecin_id
        filter_parts.append("medecin_id = :m")
    if patient_id:
        expr_values[":p"] = patient_id
        filter_parts.append("patient_id = :p")

    base_kwargs = {
        "IndexName": "EntityTypeIndex",
        "KeyConditionExpression": "EntityType = :t",
        "ExpressionAttributeValues": expr_values,
        "ScanIndexForward": False,
    }
    if filter_parts:
        base_kwargs["FilterExpression"] = " AND ".join(filter_parts)

    accumulated = []
    exclusive_start = _decode_key(start_key) if start_key else None

    while len(accumulated) < limit:
        kwargs = dict(base_kwargs)
        kwargs["Limit"] = limit
        if exclusive_start:
            kwargs["ExclusiveStartKey"] = exclusive_start

        result = table.query(**kwargs)
        items = result.get("Items", [])
        accumulated.extend(items)
        exclusive_start = result.get("LastEvaluatedKey")

        if not exclusive_start:
            break

    # Trim to exactly `limit`
    page = accumulated[:limit]
    has_more = len(accumulated) > limit or exclusive_start is not None

    return {
        "items": [_fmt_consultation(c) for c in page],
        "limit": limit,
        "next_key": _encode_key(exclusive_start) if has_more and exclusive_start else None,
        "has_more": has_more,
    }


def _fmt_consultation(c: dict) -> dict:
    return {
        "consultation_id": c.get("EntityId"),
        "patient_id": c.get("patient_id"),
        "patient_nom": c.get("patient_nom"),
        "patient_prenom": c.get("patient_prenom"),
        "date": c.get("date_debut", "")[:10] if c.get("date_debut") else "",
        "heure": c.get("date_debut", "")[11:16] if c.get("date_debut") else "",
        "motif": c.get("motif"),
        "medecin_nom": c.get("medecin_nom"),
        "medecin_prenom": c.get("medecin_prenom"),
        "medecin_specialite": c.get("medecin_specialite"),
        "statut": c.get("statut"),
    }


def get_patient_history(patient_id: str, limit: int = 20, start_key: Optional[str] = None) -> dict:
    """List consultations for a patient, paginated, most recent first.

    GSI1PK = PATIENT#<id> already scopes to this patient's items.
    FilterExpression on EntityType filters out non-consultation items.
    Accumulate across pages to fill the requested limit.
    """
    table = _get_table()

    base_kwargs = {
        "IndexName": "GSI1",
        "KeyConditionExpression": "GSI1PK = :pk",
        "FilterExpression": "EntityType = :t",
        "ExpressionAttributeValues": {
            ":pk": f"PATIENT#{patient_id}",
            ":t": "consultation",
        },
        "ScanIndexForward": False,
    }

    accumulated = []
    exclusive_start = _decode_key(start_key) if start_key else None

    while len(accumulated) < limit:
        kwargs = dict(base_kwargs)
        kwargs["Limit"] = limit
        if exclusive_start:
            kwargs["ExclusiveStartKey"] = exclusive_start

        result = table.query(**kwargs)
        items = result.get("Items", [])
        accumulated.extend(items)
        exclusive_start = result.get("LastEvaluatedKey")

        if not exclusive_start:
            break

    page = accumulated[:limit]
    has_more = len(accumulated) > limit or exclusive_start is not None

    return {
        "patient_id": patient_id,
        "items": [{
            "consultation_id": c.get("EntityId"),
            "date": c.get("date_debut", "")[:10] if c.get("date_debut") else "",
            "heure": c.get("date_debut", "")[11:16] if c.get("date_debut") else "",
            "motif": c.get("motif"),
            "medecin_nom": c.get("medecin_nom"),
            "medecin_prenom": c.get("medecin_prenom"),
            "medecin_specialite": c.get("medecin_specialite"),
            "statut": c.get("statut"),
        } for c in page],
        "limit": limit,
        "next_key": _encode_key(exclusive_start) if has_more and exclusive_start else None,
        "has_more": has_more,
    }


def get_messages(consultation_id: str) -> list:
    """Get all messages for a consultation."""
    table = _get_table()
    pk = f"CONSULTATION#{consultation_id}"
    result = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": pk, ":sk": "MSG#"},
    )
    return [{
        "sender_type": m.get("sender_type"),
        "sender_id": m.get("sender_id"),
        "contenu": m.get("contenu"),
        "date": m.get("date_envoi", ""),
        "type_contenu": m.get("type_contenu", "text"),
    } for m in result.get("Items", [])]


def toggle_disponibilite(medecin_id: str, disponible: bool) -> dict:
    """Toggle doctor availability."""
    table = _get_table()
    pk = f"USER#{medecin_id}"
    sk = f"METADATA#{medecin_id}"
    table.update_item(
        Key={"PK": pk, "SK": sk},
        UpdateExpression="SET disponible = :val",
        ExpressionAttributeValues={":val": disponible},
    )
    return {"medecin_id": medecin_id, "disponible": disponible}


def verify_password(stored: str, cleartext: str) -> bool:
    """
    Verify a password against the stored hash.
    Works with both hex and base64 formats.
    """
    import hashlib
    import base64

    parts = stored.split(".")
    if len(parts) != 2:
        return False

    hash_part, salt_part = parts
    data = cleartext.encode("utf-8")

    # Detect format: hex (salt hex 32 chars) or base64
    try:
        salt = bytes.fromhex(salt_part)
        expected = hashlib.sha256(salt + data).hexdigest()
        return hash_part == expected
    except (ValueError, TypeError):
        pass

    try:
        salt = base64.b64decode(salt_part)
        expected = base64.b64encode(hashlib.sha256(salt + data).digest()).decode()
        return hash_part == expected
    except (ValueError, TypeError):
        pass

    return False


def login(telephone: str, password: str) -> dict:
    """
    Authenticate a user by telephone + password.
    Returns EntityId on success, raises ValueError on failure.
    """
    table = _get_table()

    # Scan users to find by telephone (phone is not an index key)
    result = table.query(
        IndexName="EntityTypeIndex",
        KeyConditionExpression="EntityType = :t",
        ExpressionAttributeValues={":t": "user"},
    )

    for item in result.get("Items", []):
        if item.get("telephone") == telephone:
            stored = item.get("password", "")
            if verify_password(stored, password):
                return {
                    "user_id": item.get("EntityId"),
                    "type_user": item.get("type_user"),
                    "nom": item.get("nom"),
                    "prenom": item.get("prenom"),
                }
            raise ValueError("Mot de passe incorrect")

    raise ValueError("Aucun utilisateur trouve avec ce numero de telephone")
