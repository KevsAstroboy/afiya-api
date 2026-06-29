import pytest
from unittest.mock import AsyncMock, MagicMock
from core.workflow.checks import BusinessChecks
from core.workflow.types import CheckResult


class TestBusinessChecks:
    @pytest.mark.asyncio
    async def test_check_record_exists_found(self):
        db = MagicMock()
        db.find_one = AsyncMock(return_value={"nom": "Kone", "prenom": "Amadou"})
        checks = BusinessChecks(db)
        context = {"input_telephone": "0700000000"}
        result = await checks.check_record_exists(
            context,
            table="clients",
            lookup_key="telephone",
            context_key="input_telephone",
        )
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_check_record_exists_not_found(self):
        db = MagicMock()
        db.find_one = AsyncMock(return_value=None)
        checks = BusinessChecks(db)
        context = {"input_telephone": "0700000000"}
        result = await checks.check_record_exists(
            context,
            table="clients",
            lookup_key="telephone",
            context_key="input_telephone",
        )
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_check_fields_complete_all_present(self):
        checks = BusinessChecks(MagicMock())
        context = {"nom": "Kone", "prenom": "Amadou", "email": "test@test.com"}
        result = await checks.check_fields_complete(
            context,
            fields=["nom", "prenom", "email"],
            source="context",
        )
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_check_fields_complete_missing(self):
        checks = BusinessChecks(MagicMock())
        context = {"nom": "Kone"}
        result = await checks.check_fields_complete(
            context,
            fields=["nom", "prenom", "email"],
            source="context",
        )
        assert result.passed is False
        assert "prenom" in result.data["missing_fields"]

    @pytest.mark.asyncio
    async def test_check_payment_status_confirmed(self):
        db = MagicMock()
        db.find_one = AsyncMock(return_value={"status": "confirmed", "amount": 15000})
        checks = BusinessChecks(db)
        context = {"input_transaction_id": "TXN-001"}
        result = await checks.check_payment_status(
            context,
            context_key="input_transaction_id",
            expected_status="confirmed",
        )
        assert result.passed is True
        assert "db_payment_record" in context

    @pytest.mark.asyncio
    async def test_check_payment_status_wrong_status(self):
        db = MagicMock()
        db.find_one = AsyncMock(return_value={"status": "pending"})
        checks = BusinessChecks(db)
        context = {"input_transaction_id": "TXN-001"}
        result = await checks.check_payment_status(
            context,
            context_key="input_transaction_id",
            expected_status="confirmed",
        )
        assert result.passed is False
