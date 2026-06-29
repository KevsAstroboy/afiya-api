import pytest
from core.repository.interface import RepositoryInterface


class TestRepositoryInterface:
    def test_interface_has_required_methods(self):
        methods = ["create", "get_by_id", "get_all", "update", "delete", "find_one", "find_by"]
        for method in methods:
            assert hasattr(RepositoryInterface, method)
            assert callable(getattr(RepositoryInterface, method))
