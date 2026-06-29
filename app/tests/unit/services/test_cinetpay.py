import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.cinetpay.cinetpay_service import CinetPayService


class TestCinetPayService:
    def test_validate_ipn_signature_valid(self, monkeypatch):
        monkeypatch.setattr("services.cinetpay.cinetpay_service.settings.CINETPAY_SECRET_KEY", "mysecret")
        service = CinetPayService()
        payload = {"cpm_trans_id": "TXN-001", "cpm_result": "00"}
        import hashlib
        import hmac
        sorted_keys = sorted(payload.keys())
        signature_data = "".join(f"{k}={payload[k]}" for k in sorted_keys)
        computed = hmac.new(
            b"mysecret", signature_data.encode("utf-8"), hashlib.sha256
        ).hexdigest().upper()
        assert service.validate_ipn_signature(payload, computed) is True

    def test_validate_ipn_signature_invalid(self, monkeypatch):
        monkeypatch.setattr("services.cinetpay.cinetpay_service.settings.CINETPAY_SECRET_KEY", "mysecret")
        service = CinetPayService()
        payload = {"cpm_trans_id": "TXN-001", "cpm_result": "00"}
        assert service.validate_ipn_signature(payload, "bad_signature") is False
