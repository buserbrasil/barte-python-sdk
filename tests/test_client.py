import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from dacite import from_dict
from barte import BarteClient, Charge, CardToken, Refund, InstallmentOptions, PixCharge
from barte.models import DACITE_CONFIG


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
            "email": "john@example.com",
        },
        "created_at": "2024-01-07T10:00:00Z",
        "metadata": {"order_id": "123"},
    }


class TestBarteClient:
    def test_client_initialization(self):
        """Test client initialization with valid environment"""
        client = BarteClient(api_key="test_key", environment="sandbox")
        assert client.api_key == "test_key"
        assert client.base_url == "https://sandbox-api.barte.com"
        assert client.headers == {
            "X-Token-Api": "test_key",
            "Content-Type": "application/json",
        }

    def test_invalid_environment(self):
        """Test client initialization with invalid environment"""
        with pytest.raises(ValueError) as exc_info:
            BarteClient(api_key="test_key", environment="invalid")
        assert "Invalid environment" in str(exc_info.value)

    @patch("requests.post")
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
                "email": "john@example.com",
            },
        }

        charge = barte_client.create_charge(charge_data)

        assert isinstance(charge, Charge)
        assert charge.amount == 1000
        assert charge.customer.name == "John Doe"
        assert charge.metadata == {"order_id": "123"}
        assert isinstance(charge.created_at, datetime)

        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=charge_data,
        )

    @patch("requests.post")
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
                "email": "john@example.com",
            },
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
            json=expected_data,
        )

    @patch("requests.post")
    def test_create_card_token(self, mock_post, barte_client):
        """Test creating a card token"""
        mock_response = {
            "uuid": "790e8637-c16b-4ed5-a9bf-faec76dbc5aa",
            "status": "ACTIVE",
            "createdAt": "2025-02-07",
            "brand": "mastercard",
            "cardHolderName": "John Doe",
            "cvvChecked": True,
            "fingerprint": "MLvWOfRXBcGIvK9cWSj9vLy0yhmBMzbxldLSJHYvEEw=",
            "first6digits": "538363",
            "last4digits": "0891",
            "buyerId": "5929a30b-e68f-4c81-9481-d25adbabafeb",
            "expirationMonth": "12",
            "expirationYear": "2025",
            "cardId": "9dc2ffe0-d588-44b7-b74d-d5ad88a31143",
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        card_data = {
            "number": "5383630891",
            "holder_name": "John Doe",
            "expiration_month": 12,
            "expiration_year": 2025,
            "cvv": "123",
        }

        token = barte_client.create_card_token(card_data)

        assert isinstance(token, CardToken)
        assert token.uuid == "790e8637-c16b-4ed5-a9bf-faec76dbc5aa"
        assert token.last4digits == "0891"
        assert token.cardHolderName == "John Doe"
        assert isinstance(token.createdAt, datetime)

        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v2/cards",
            headers=barte_client.headers,
            json=card_data,
        )

    @patch("requests.get")
    def test_simulate_installments(self, mock_get, barte_client):
        """Test installment simulation"""
        mock_response = {
            "installments": [
                {
                    "installments": 1,
                    "amount": 1000,
                    "total": 1000,
                    "interest_rate": 0.0,
                },
                {"installments": 2, "amount": 510, "total": 1020, "interest_rate": 2.0},
                {"installments": 3, "amount": 345, "total": 1035, "interest_rate": 3.5},
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
            params={"amount": 1000, "brand": "visa"},
        )

    @patch("requests.post")
    def test_refund_charge(self, mock_post, barte_client):
        """Test refunding a charge"""
        mock_response = {
            "id": "ref_123456",
            "charge_id": "chr_123456789",
            "amount": 1000,
            "status": "succeeded",
            "created_at": "2024-01-07T10:00:00Z",
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
            json=refund_data,
        )

    @patch("requests.get")
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
            headers=barte_client.headers,
        )

    @patch("requests.get")
    def test_list_charges(self, mock_get, barte_client, mock_charge_response):
        """Test listing all charges"""
        mock_response = {
            "data": [
                mock_charge_response,
                {**mock_charge_response, "id": "chr_987654321"},
            ],
            "has_more": False,
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        params = {"limit": 2, "starting_after": "chr_0"}
        charges = barte_client.list_charges(params)

        assert len(charges) == 2
        assert all(isinstance(charge, Charge) for charge in charges)
        assert charges[0].id == "chr_123456789"
        assert charges[1].id == "chr_987654321"
        assert all(isinstance(charge.created_at, datetime) for charge in charges)

        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            params=params,
        )

    @patch("requests.post")
    def test_charge_methods(self, mock_post, mock_charge_response):
        """Test charge instance methods"""
        # Mock for refund
        refund_response = {
            "id": "ref_123456",
            "charge_id": "chr_123456789",
            "amount": 500,
            "status": "succeeded",
            "created_at": "2024-01-07T10:00:00Z",
        }
        mock_post.return_value.json.return_value = refund_response
        mock_post.return_value.raise_for_status = Mock()

        charge = from_dict(
            data_class=Charge, data=mock_charge_response, config=DACITE_CONFIG
        )

        # Test refund method
        refund = charge.refund(amount=500)
        assert isinstance(refund, Refund)
        assert refund.amount == 500
        mock_post.assert_called_with(
            f"https://sandbox-api.barte.com/v1/charges/{charge.id}/refund",
            headers={"X-Token-Api": "test_key", "Content-Type": "application/json"},
            json={"amount": 500},
        )

        # Mock for cancel - use the original mock response with updated status
        cancel_response = {**mock_charge_response, "status": "canceled"}
        mock_post.return_value.json.return_value = cancel_response

        # Test cancel method
        canceled_charge = charge.cancel()
        assert isinstance(canceled_charge, Charge)
        assert canceled_charge.status == "canceled"
        mock_post.assert_called_with(
            f"https://sandbox-api.barte.com/v1/charges/{charge.id}/cancel",
            headers={"X-Token-Api": "test_key", "Content-Type": "application/json"},
        )

    @patch("requests.get")
    def test_pix_charge_get_qrcode(self, mock_get, mock_charge_response):
        """Test PIX charge QR code method"""
        # Create a PIX charge
        pix_charge = from_dict(
            data_class=PixCharge,
            data={**mock_charge_response, "payment_method": "pix"},
            config=DACITE_CONFIG,
        )

        # Mock QR code response
        qr_code_response = {
            "qr_code": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000",
            "qr_code_image": "https://api.barte.com/v1/qrcodes/123456.png",
            "copy_and_paste": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000",
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
            f"https://sandbox-api.barte.com/v1/charges/{pix_charge.id}/pix",
            headers={"X-Token-Api": "test_key", "Content-Type": "application/json"},
        )

    def test_client_singleton(self):
        """Test client singleton pattern"""
        # Reset singleton for initial state
        BarteClient._instance = None

        # Test uninitialized state
        with pytest.raises(RuntimeError) as exc_info:
            BarteClient.get_instance()
        assert "BarteClient not initialized" in str(exc_info.value)

        # First initialization
        client1 = BarteClient(api_key="test_key", environment="sandbox")
        assert BarteClient.get_instance() == client1

        # Second initialization
        client2 = BarteClient(api_key="another_key", environment="sandbox")
        assert BarteClient.get_instance() == client2
        assert client2.api_key == "another_key"

        # Reset singleton for other tests
        BarteClient._instance = None

    @patch("requests.post")
    def test_charge_with_card_token(
        self, mock_post, barte_client, mock_charge_response
    ):
        """Test creating a charge with card token"""
        mock_post.return_value.json.return_value = mock_charge_response
        mock_post.return_value.raise_for_status = Mock()

        token_id = "tok_123456"
        charge_data = {
            "amount": 1000,
            "description": "Test charge with token",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com",
            },
            "metadata": {"order_id": "123"},
        }

        charge = barte_client.charge_with_card_token(token_id, charge_data)

        assert isinstance(charge, Charge)
        assert charge.amount == 1000
        assert charge.customer.name == "John Doe"
        assert charge.metadata == {"order_id": "123"}
        assert isinstance(charge.created_at, datetime)

        expected_data = {
            **charge_data,
            "payment_method": "credit_card",
            "card_token": token_id,
        }
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data,
        )

    @patch("requests.get")
    def test_get_charge_refunds(self, mock_get, barte_client):
        """Test getting refunds for a charge"""
        mock_response = {
            "data": [
                {
                    "id": "ref_123456",
                    "charge_id": "chr_123456789",
                    "amount": 500,
                    "status": "succeeded",
                    "created_at": "2024-01-07T10:00:00Z",
                },
                {
                    "id": "ref_789012",
                    "charge_id": "chr_123456789",
                    "amount": 500,
                    "status": "succeeded",
                    "created_at": "2024-01-07T10:30:00Z",
                },
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        refunds = barte_client.get_charge_refunds("chr_123456789")

        assert len(refunds) == 2
        assert all(isinstance(refund, Refund) for refund in refunds)
        assert refunds[0].id == "ref_123456"
        assert refunds[1].id == "ref_789012"
        assert refunds[0].amount == 500
        assert refunds[1].status == "succeeded"
        assert all(isinstance(refund.created_at, datetime) for refund in refunds)

        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/refunds",
            headers=barte_client.headers,
        )

    @patch("requests.get")
    def test_get_charge_refunds_empty(self, mock_get, barte_client):
        """Test getting refunds for a charge with no refunds"""
        mock_response = {"data": []}
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        refunds = barte_client.get_charge_refunds("chr_123456789")

        assert len(refunds) == 0
        assert isinstance(refunds, list)

        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/refunds",
            headers=barte_client.headers,
        )

    @patch("requests.post")
    def test_charge_with_card_token_with_installments(
        self, mock_post, barte_client, mock_charge_response
    ):
        """Test creating a charge with card token and installments"""
        response_with_installments = {
            **mock_charge_response,
            "installments": 3,
            "installment_amount": 333,
        }
        mock_post.return_value.json.return_value = response_with_installments
        mock_post.return_value.raise_for_status = Mock()

        token_id = "tok_123456"
        charge_data = {
            "amount": 1000,
            "description": "Test charge with installments",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com",
            },
            "installments": 3,
        }

        charge = barte_client.charge_with_card_token(token_id, charge_data)

        assert isinstance(charge, Charge)
        assert charge.amount == 1000
        assert charge.installments == 3
        assert charge.installment_amount == 333
        assert charge.customer.name == "John Doe"
        assert isinstance(charge.created_at, datetime)

        expected_data = {
            **charge_data,
            "payment_method": "credit_card",
            "card_token": token_id,
        }
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data,
        )
