import json
import logging
from typing import List, Optional

from core.workflow.providers.bedrock import BedrockAnthropicProvider

logger = logging.getLogger(__name__)


async def generate_resume_ia(
    messages: List[str],
    patient_nom: str = "",
    motif: str = "",
    provider: Optional[BedrockAnthropicProvider] = None,
    model: str = "anthropic.claude-sonnet-4-6",
) -> dict:
    """
    Analyze consultation messages and generate a structured medical summary.

    Args:
        messages: List of message texts from the consultation
        patient_nom: Patient's full name
        motif: Reason for consultation
        provider: BedrockAnthropicProvider instance (created if None)
        model: Bedrock model ID

    Returns:
        dict with keys: symptomes, facteurs_risque, niveau_risque, recommandation, resume
    """
    if provider is None:
        provider = BedrockAnthropicProvider()

    conversation = "\n".join(
        f"[{i+1}] {msg}" for i, msg in enumerate(messages[:30])
    )

    prompt = f"""Tu es un assistant medical qui analyse les conversations entre un patient et un medecin.

Patient : {patient_nom or 'Patient'}
Motif de consultation : {motif or 'Non specifie'}

Conversation :
{conversation}

Analyse cette conversation et retourne UNIQUEMENT un objet JSON valide avec ce format exact :
{{
  "symptomes": ["symptome1", "symptome2"],
  "facteurs_risque": ["facteur1", "facteur2"],
  "niveau_risque": "FAIBLE|MODERE|ELEVE|CRITIQUE",
  "recommandation": "recommandation medicale en 1-2 phrases",
  "resume": "resume de la consultation en 2-3 phrases"
}}

Regles :
- Symptomes : extrais les symptomes mentionnes par le patient (max 5, sois precis)
- Facteurs de risque : deduis les facteurs de risque potentiels (max 3)
- Niveau de risque : FAIBLE (consultation de routine), MODERE (necessite suivi), ELEVE (examens urgents), CRITIQUE (danger immediat)
- Recommandation : suggestion concrete pour le patient
- Resume : synthese claire de l'echange en francais
- AUCUN autre texte avant ou apres le JSON
"""

    try:
        response = await provider.generate(prompt, model, 800)

        # Parse JSON from response (handle markdown code blocks)
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        response = response.strip()

        result = json.loads(response)

        logger.info("Resume IA genere pour consultation")
        return {
            "symptomes": result.get("symptomes", []),
            "facteurs_risque": result.get("facteurs_risque", []),
            "niveau_risque": result.get("niveau_risque", "MODERE"),
            "recommandation": result.get("recommandation", ""),
            "resume": result.get("resume", ""),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse resume IA response: {e}\nResponse: {response}")
        return {
            "symptomes": [],
            "facteurs_risque": [],
            "niveau_risque": "MODERE",
            "recommandation": "Consultation de suivi recommandee.",
            "resume": "Impossible de generer le resume automatiquement.",
        }
    except Exception as e:
        logger.exception(f"Erreur generation resume IA: {e}")
        return {
            "symptomes": [],
            "facteurs_risque": [],
            "niveau_risque": "MODERE",
            "recommandation": "Consultation de suivi recommandee.",
            "resume": "Erreur lors de la generation du resume.",
        }
