import pytest
from barte import BarteClient


@pytest.fixture
def barte_client():
    """Fixture that provides a Barte client instance for testing"""
    return BarteClient(api_key="test_api_key_123", environment="sandbox")


@pytest.fixture
def mock_response():
    """Fixture that provides a mock response structure"""
    return {
        "id": "chr_123456789",
        "status": "pending",
        "created_at": "2024-03-20T10:00:00Z",
        "amount": 1000,
        "currency": "BRL",
        "description": "Test charge",
    }
