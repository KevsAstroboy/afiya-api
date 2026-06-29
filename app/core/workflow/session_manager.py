import logging
import uuid
from datetime import datetime, timezone

from core.workflow.redis_session import RedisSessionStore, RESET_KEYWORDS
from core.workflow.engine import NON_INTERACTIVE_STEPS

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, store: RedisSessionStore, engine, db):
        self.store = store
        self.engine = engine
        self.db = db

    async def handle_message(self, wa_id: str, message: str, nom_whatsapp: str = "") -> str:
        if message.strip().lower() in RESET_KEYWORDS:
            self.store.delete(wa_id)
            return await self._start(wa_id, nom_whatsapp)

        if not self.store.exists(wa_id):
            return await self._start(wa_id, nom_whatsapp)

        state = self.store.get_field(wa_id, "state")
        if state == "complet":
            return "Votre dossier est deja complet. Envoyez *recommencer* pour en creer un nouveau."

        return await self._process(wa_id, message)

    async def _start(self, wa_id: str, nom_whatsapp: str) -> str:
        patient = await self.db.find_one("user", {"telephone": f"+{wa_id}"})

        self.store.init(wa_id, {
            "wa_id": wa_id,
            "nom_whatsapp": nom_whatsapp,
            "state": "en_cours",
            "current_step_id": "step-accueil",
            "last_message_at": datetime.now(timezone.utc).isoformat(),
            "patient_existant": patient is not None,
            "db_user_record": patient or {},
            "patient_nom": patient.get("nom", "") if patient else "",
            "patient_prenom": patient.get("prenom", "") if patient else "",
        })

        logger.info("[SESSION] Demarrage : %s | existant=%s", wa_id, patient is not None)
        return (
            f"Bonjour {nom_whatsapp}, bienvenue chez *Afiya* !\n\n"
            "Etes-vous la pour une consultation ? _(oui / non)_"
        )

    async def _process(self, wa_id: str, message: str) -> str:
        context = self.store.get(wa_id)
        step_id = context.get("current_step_id")
        self.store.set_field(wa_id, "last_message_at", datetime.now(timezone.utc).isoformat())
        context["user_input"] = message

        result = None

        while step_id:
            result = await self.engine.run_single_step(
                workflow_id="wf-patient-collecte",
                step_id=step_id,
                context=context,
            )

            if result["status"] == "success":
                key = result.get("collected_key")
                value = result.get("collected_value")
                if key and value is not None:
                    self.store.set_field(wa_id, key, value)

                next_step_id = result.get("next_step_id")

                if not next_step_id:
                    await self._finalize(wa_id)
                    break

                next_step = await self.engine.get_step("wf-patient-collecte", next_step_id)
                self.store.set_field(wa_id, "current_step_id", next_step_id)
                context = self.store.get(wa_id)

                if next_step.step_type in NON_INTERACTIVE_STEPS:
                    step_id = next_step_id
                    continue
                else:
                    break
            else:
                break

        return result["whatsapp_reply"] if result else "Une erreur est survenue."

    async def _finalize(self, wa_id: str) -> None:
        context = self.store.get(wa_id)

        if not context.get("patient_existant"):
            patient_id = str(uuid.uuid4())
            await self.db.insert("user", {
                "id": patient_id,
                "telephone": f"+{wa_id}",
                "nom": context.get("patient_nom", ""),
                "prenom": context.get("patient_prenom", ""),
                "type_user": "PATIENT",
                "sexe_id": 1,
                "statut_id": 1,
                "email": f"{wa_id}@afiya.ci",
                "password": "changeme",
                "annee_naissance": 2000,
                "lieu_naissance": "",
            })

        self.store.set_field(wa_id, "state", "complet")
        logger.info("[SESSION] Dossier finalise : wa_id=%s", wa_id)
