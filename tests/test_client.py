import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from barte import BarteClient, Charge, CardToken, Refund, InstallmentOptions, PixCharge

@pytest.fixture
def barte_client():
    client = BarteClient(api_key="test_key", environment="sandbox")
    BarteClient._instance = client  # Set instance for model methods
    return client

@pytest.fixture
def mock_charge_response():
    return {
        "id": "chr_123456789",
        "amount": 1000,
        "currency": "BRL",
        "status": "succeeded",
        "payment_method": "credit_card",
        "description": "Test charge",
        "customer": {
            "name": "John Doe",
            "tax_id": "123.456.789-00",
            "email": "john@example.com"
        },
        "created_at": "2024-01-07T10:00:00Z",
        "metadata": {"order_id": "123"}
    }

class TestBarteClient:
    def test_client_initialization(self):
        """Test client initialization with different environments"""
        # Production environment
        client = BarteClient(api_key="test_key", environment="production")
        assert client.base_url == "https://api.barte.com.br"
        
        # Sandbox environment
        client = BarteClient(api_key="test_key", environment="sandbox")
        assert client.base_url == "https://sandbox-api.barte.com.br"
        
        # Check headers
        assert client.headers["Authorization"] == "Bearer test_key"
        assert client.headers["Content-Type"] == "application/json"

    @patch('requests.post')
    def test_create_charge(self, mock_post, barte_client, mock_charge_response):
        """Test creating a new charge"""
        mock_post.return_value.json.return_value = mock_charge_response
        mock_post.return_value.raise_for_status = Mock()

        charge_data = {
            "amount": 1000,
            "description": "Test charge",
            "payment_method": "credit_card",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            }
        }

        charge = barte_client.create_charge(charge_data)
        
        assert isinstance(charge, Charge)
        assert charge.id == "chr_123456789"
        assert charge.amount == 1000
        assert charge.status == "succeeded"
        assert charge.customer.name == "John Doe"
        
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=charge_data
        )

    @patch('requests.post')
    def test_create_pix_charge(self, mock_post, barte_client, mock_charge_response):
        """Test creating a PIX charge"""
        pix_response = {**mock_charge_response, "payment_method": "pix"}
        mock_post.return_value.json.return_value = pix_response
        mock_post.return_value.raise_for_status = Mock()

        pix_data = {
            "amount": 1000,
            "description": "PIX Test",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            }
        }

        charge = barte_client.create_pix_charge(pix_data)
        
        assert isinstance(charge, PixCharge)
        assert charge.payment_method == "pix"
        assert charge.amount == 1000
        assert charge.customer.name == "John Doe"
        
        expected_data = {**pix_data, "payment_method": "pix"}
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data
        )

    @patch('requests.post')
    def test_create_card_token(self, mock_post, barte_client):
        """Test creating a card token"""
        mock_response = {
            "id": "tok_123456",
            "type": "card",
            "created_at": "2024-03-20T10:00:00Z",
            "last_digits": "1111",
            "holder_name": "John Doe",
            "expiration_month": 12,
            "expiration_year": 2025,
            "brand": "visa"
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        card_data = {
            "number": "4111111111111111",
            "holder_name": "John Doe",
            "expiration_month": 12,
            "expiration_year": 2025,
            "cvv": "123"
        }

        token = barte_client.create_card_token(card_data)
        
        assert isinstance(token, CardToken)
        assert token.id == "tok_123456"
        assert token.last_digits == "1111"
        assert token.holder_name == "John Doe"
        assert isinstance(token.created_at, datetime)
        
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/tokens",
            headers=barte_client.headers,
            json=card_data
        )

    @patch('requests.get')
    def test_simulate_installments(self, mock_get, barte_client):
        """Test installment simulation"""
        mock_response = {
            "installments": [
                {"installments": 1, "amount": 1000, "total": 1000, "interest_rate": 0.0},
                {"installments": 2, "amount": 510, "total": 1020, "interest_rate": 2.0},
                {"installments": 3, "amount": 345, "total": 1035, "interest_rate": 3.5}
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        options = barte_client.simulate_installments(amount=1000, brand="visa")
        
        assert isinstance(options, InstallmentOptions)
        assert len(options.installments) == 3
        assert options.installments[0].amount == 1000
        assert options.installments[1].interest_rate == 2.0
        
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/simulate/installments",
            headers=barte_client.headers,
            params={"amount": 1000, "brand": "visa"}
        )

    @patch('requests.post')
    def test_refund_charge(self, mock_post, barte_client):
        """Test refunding a charge"""
        mock_response = {
            "id": "ref_123456",
            "charge_id": "chr_123456789",
            "amount": 1000,
            "status": "succeeded",
            "created_at": "2024-01-07T10:00:00Z"
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        refund_data = {"amount": 1000}
        refund = barte_client.refund_charge("chr_123456789", refund_data)
        
        assert isinstance(refund, Refund)
        assert refund.id == "ref_123456"
        assert refund.amount == 1000
        assert refund.status == "succeeded"
        assert isinstance(refund.created_at, datetime)
        
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/refund",
            headers=barte_client.headers,
            json=refund_data
        )

    def test_invalid_environment(self):
        """Test initialization with invalid environment"""
        with pytest.raises(ValueError):
            BarteClient(api_key="test_key", environment="invalid")

    @patch('requests.get')
    def test_get_charge(self, mock_get, barte_client, mock_charge_response):
        """Test getting a specific charge"""
        mock_get.return_value.json.return_value = mock_charge_response
        mock_get.return_value.raise_for_status = Mock()

        charge = barte_client.get_charge("chr_123456789")
        
        assert isinstance(charge, Charge)
        assert charge.id == "chr_123456789"
        assert charge.amount == 1000
        assert charge.customer.name == "John Doe"
        assert isinstance(charge.created_at, datetime)
        
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789",
            headers=barte_client.headers
        )

    @patch('requests.get')
    def test_list_charges(self, mock_get, barte_client, mock_charge_response):
        """Test listing all charges"""
        mock_response = {
            "data": [mock_charge_response, {**mock_charge_response, "id": "chr_987654321"}],
            "has_more": False
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        params = {"limit": 2, "starting_after": "chr_0"}
        charges = barte_client.list_charges(params)
        
        assert len(charges) == 2
        assert all(isinstance(charge, Charge) for charge in charges)
        assert charges[0].id == "chr_123456789"
        assert charges[1].id == "chr_987654321"
        
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            params=params
        )

    @patch('requests.post')
    def test_charge_methods(self, mock_post, mock_charge_response):
        """Test charge instance methods"""
        # Mock for refund
        refund_response = {
            "id": "ref_123456",
            "charge_id": "chr_123456789",
            "amount": 500,
            "status": "succeeded",
            "created_at": "2024-01-07T10:00:00Z"
        }
        mock_post.return_value.json.return_value = refund_response
        mock_post.return_value.raise_for_status = Mock()

        charge = Charge.from_dict(mock_charge_response)
        
        # Test refund method
        refund = charge.refund(amount=500)
        assert isinstance(refund, Refund)
        assert refund.amount == 500
        mock_post.assert_called_with(
            f"https://sandbox-api.barte.com.br/v1/charges/{charge.id}/refund",
            headers={"Authorization": "Bearer test_key", "Content-Type": "application/json"},
            json={"amount": 500}
        )
        
        # Mock for cancel - use the original mock response with updated status
        cancel_response = {
            **mock_charge_response,
            "status": "canceled"
        }
        mock_post.return_value.json.return_value = cancel_response
        
        # Test cancel method
        canceled_charge = charge.cancel()
        assert isinstance(canceled_charge, Charge)
        assert canceled_charge.status == "canceled"
        mock_post.assert_called_with(
            f"https://sandbox-api.barte.com.br/v1/charges/{charge.id}/cancel",
            headers={"Authorization": "Bearer test_key", "Content-Type": "application/json"}
        )

    @patch('requests.get')
    def test_pix_charge_get_qrcode(self, mock_get, mock_charge_response):
        """Test PIX charge QR code method"""
        # Create a PIX charge
        pix_charge = PixCharge.from_dict({**mock_charge_response, "payment_method": "pix"})
        
        # Mock QR code response
        qr_code_response = {
            "qr_code": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000",
            "qr_code_image": "https://api.barte.com.br/v1/qrcodes/123456.png",
            "copy_and_paste": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000"
        }
        mock_get.return_value.json.return_value = qr_code_response
        mock_get.return_value.raise_for_status = Mock()

        # Get QR code
        pix_charge = pix_charge.get_qr_code()
        
        assert isinstance(pix_charge, PixCharge)
        assert pix_charge.qr_code == qr_code_response["qr_code"]
        assert pix_charge.qr_code_image == qr_code_response["qr_code_image"]
        assert pix_charge.copy_and_paste == qr_code_response["copy_and_paste"]
        
        mock_get.assert_called_once_with(
            f"https://sandbox-api.barte.com.br/v1/charges/{pix_charge.id}/pix",
            headers={"Authorization": "Bearer test_key", "Content-Type": "application/json"}
        )

    def test_client_singleton(self):
        """Test client singleton pattern"""
        # Should raise error when not initialized
        BarteClient._instance = None
        with pytest.raises(RuntimeError):
            BarteClient.get_instance()
        
        # Should return same instance after initialization
        client1 = BarteClient(api_key="test_key", environment="sandbox")
        client2 = BarteClient.get_instance()
        assert client1 is client2 