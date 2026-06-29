from core.workflow.types import CheckResult


class BusinessChecks:
    def __init__(self, db):
        self.db = db

    async def check_record_exists(self, context: dict, **config) -> CheckResult:
        table = config["table"]
        lookup_key = config["lookup_key"]
        value = context.get(config["context_key"])
        if value is None:
            return CheckResult(False, f"Valeur manquante dans le contexte : '{config['context_key']}'")
        record = await self.db.find_one(table, {lookup_key: value})
        if not record:
            return CheckResult(False, f"Aucun enregistrement dans '{table}' ou {lookup_key}='{value}'")
        context[f"db_{table}_record"] = record
        return CheckResult(True, "Enregistrement trouve", data=record)

    async def check_fields_complete(self, context: dict, **config) -> CheckResult:
        fields = config["fields"]
        source = config.get("source", "context")
        data = context if source == "context" else (context.get(config.get("record_key")) or {})
        missing = [f for f in fields if not data.get(f)]
        if missing:
            return CheckResult(False, f"Champs manquants : {missing}", data={"missing_fields": missing})
        return CheckResult(True, "Tous les champs sont renseignes")

    async def check_payment_status(self, context: dict, **config) -> CheckResult:
        transaction_id = context.get(config["context_key"])
        expected_status = config.get("expected_status", "confirmed")
        if not transaction_id:
            return CheckResult(False, f"transaction_id absent du contexte : '{config['context_key']}'")
        payment = await self.db.find_one("paiement", {"transaction_id": transaction_id})
        if not payment:
            return CheckResult(False, f"Paiement introuvable : {transaction_id}")
        actual = payment.get("status") if isinstance(payment, dict) else getattr(payment, "status", None)
        if actual != expected_status:
            return CheckResult(
                False,
                f"Statut invalide — attendu: '{expected_status}' | actuel: '{actual}'",
                data={"payment": payment},
            )
        context["db_payment_record"] = payment
        return CheckResult(True, "Paiement confirme", data=payment)
