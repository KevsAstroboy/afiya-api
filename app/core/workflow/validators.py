import re
import logging
from datetime import datetime, date
from typing import Callable, Optional

from core.workflow.types import ValidationResult

logger = logging.getLogger(__name__)


class Validators:
    def __init__(self):
        self._registry: dict[str, Callable] = {
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance,
            "poids": self.poids,
            "taille": self.taille,
            "expected_values": self.expected_values,
            "telephone": self.telephone,
            "temperature": self.temperature,
        }

    def get(self, name: str) -> Optional[Callable]:
        return self._registry.get(name)

    def register(self, name: str, fn: Callable) -> None:
        self._registry[name] = fn

    def nom(self, raw: str, **_) -> ValidationResult:
        value = raw.strip().upper()
        if not re.match(r"^[A-Z\u00C0-\u017F\s\-']{2,50}$", value):
            return ValidationResult(valid=False, reason=f"'{raw}' ne semble pas etre un nom valide. Lettres uniquement, 2 a 50 caracteres.")
        return ValidationResult(valid=True, value=value)

    def prenom(self, raw: str, **_) -> ValidationResult:
        value = raw.strip().title()
        if not re.match(r"^[A-Za-z\u00C0-\u017F\s\-']{2,50}$", value):
            return ValidationResult(valid=False, reason=f"'{raw}' ne semble pas etre un prenom valide.")
        return ValidationResult(valid=True, value=value)

    def date_naissance(self, raw: str, **_) -> ValidationResult:
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %m %Y"]
        raw = raw.strip()
        for fmt in formats:
            try:
                parsed = datetime.strptime(raw, fmt).date()
                age = (date.today() - parsed).days // 365
                if not (0 < age < 130):
                    return ValidationResult(valid=False, reason=f"Date incoherente — age calcule : {age} ans.")
                return ValidationResult(valid=True, value=parsed.isoformat())
            except ValueError:
                continue
        return ValidationResult(valid=False, reason=f"Format non reconnu : '{raw}'. Essayez JJ/MM/AAAA (ex: 14/05/1990).")

    def poids(self, raw: str, **_) -> ValidationResult:
        try:
            value = float(raw.strip().replace(",", ".").replace("kg", "").strip())
            if not (1 <= value <= 300):
                return ValidationResult(valid=False, reason=f"{value} kg semble hors plage. Entrez un poids entre 1 et 300 kg.")
            return ValidationResult(valid=True, value=round(value, 1))
        except ValueError:
            return ValidationResult(valid=False, reason=f"'{raw}' n'est pas un poids valide. Entrez un nombre (ex: 72 ou 72.5).")

    def taille(self, raw: str, **_) -> ValidationResult:
        try:
            cleaned = raw.strip().replace(",", ".").replace("cm", "").replace("m", "").strip()
            value = float(cleaned)
            if value < 3:
                value = round(value * 100, 1)
            if not (50 <= value <= 250):
                return ValidationResult(valid=False, reason=f"{value} cm semble hors plage. Entrez une taille entre 50 et 250 cm.")
            return ValidationResult(valid=True, value=round(value, 1))
        except ValueError:
            return ValidationResult(valid=False, reason=f"'{raw}' n'est pas une taille valide. Entrez un nombre (ex: 175 ou 1.75).")

    def telephone(self, raw: str, **_) -> ValidationResult:
        cleaned = re.sub(r"[\s\-\.\(\)]", "", raw.strip())
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        if not re.match(r"^\d{8,15}$", cleaned):
            return ValidationResult(valid=False, reason=f"'{raw}' ne semble pas etre un numero valide. Ex: 0700000000")
        return ValidationResult(valid=True, value=cleaned)

    def temperature(self, raw: str, **_) -> ValidationResult:
        try:
            value = float(raw.strip().replace(",", ".").replace("°c", "").replace("°", "").strip())
            if not (34.0 <= value <= 42.5):
                return ValidationResult(valid=False, reason=f"{value}°C semble hors plage. Attendu entre 34 et 42.5°C.")
            return ValidationResult(valid=True, value=round(value, 1))
        except ValueError:
            return ValidationResult(valid=False, reason=f"'{raw}' n'est pas une temperature valide. Ex: 37.5")

    def expected_values(self, raw: str, expected_values=None, case_sensitive: bool = False, value_map: dict = None, **_) -> ValidationResult:
        if not expected_values:
            return ValidationResult(valid=False, reason="Aucune valeur attendue configuree.")
        value = raw.strip() if case_sensitive else raw.strip().lower()
        normalized = expected_values if case_sensitive else [e.lower() for e in expected_values]
        if value not in normalized:
            return ValidationResult(valid=False, reason=f"Reponse '{raw}' non reconnue. Options valides : {' | '.join(expected_values)}")
        idx = normalized.index(value)
        original = expected_values[idx]
        final_value = value_map.get(original, original) if value_map else original
        return ValidationResult(valid=True, value=final_value)
