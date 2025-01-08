import pytest
import os
from barte import BarteClient

# Skip these tests if no API key is provided
pytestmark = pytest.mark.skipif(
    not os.getenv("BARTE_API_KEY"),
    reason="No API key provided for integration tests"
)

class TestBarteIntegration:
    @pytest.fixture
    def client(self):
        return BarteClient(
            api_key=os.getenv("BARTE_API_KEY"),
            environment="sandbox"
        )

    def test_create_and_fetch_charge(self, client):
        """Integration test for creating and fetching a charge"""
        # Create charge
        charge_data = {
            "amount": 1000,
            "description": "Integration Test Charge",
            "payment_method": "pix",
            "customer": {
                "name": "Integration Test",
                "tax_id": "123.456.789-00",
                "email": "test@example.com"
            }
        }
        
        charge = client.create_charge(charge_data)
        assert charge["status"] in ["pending", "processing"]
        
        # Fetch charge
        fetched_charge = client.get_charge(charge["id"])
        assert fetched_charge["id"] == charge["id"] 