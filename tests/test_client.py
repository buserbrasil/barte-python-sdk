import pytest
from unittest.mock import patch, Mock
from barte import BarteClient

@pytest.fixture
def barte_client():
    return BarteClient(api_key="test_key", environment="sandbox")

@pytest.fixture
def mock_response():
    return {
        "id": "chr_123456789",
        "amount": 1000,
        "status": "succeeded"
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
    def test_create_charge(self, mock_post, barte_client, mock_response):
        """Test creating a new charge"""
        mock_post.return_value.json.return_value = mock_response
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

        response = barte_client.create_charge(charge_data)
        
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=charge_data
        )

    @patch('requests.post')
    def test_create_pix_charge(self, mock_post, barte_client, mock_response):
        """Test creating a PIX charge"""
        mock_post.return_value.json.return_value = mock_response
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

        response = barte_client.create_pix_charge(pix_data)
        
        expected_data = {**pix_data, "payment_method": "pix"}
        assert response == mock_response
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
            "created_at": "2024-03-20T10:00:00Z"
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

        response = barte_client.create_card_token(card_data)
        
        assert response == mock_response
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
                {"installments": 1, "amount": 1000, "total": 1000},
                {"installments": 2, "amount": 510, "total": 1020},
                {"installments": 3, "amount": 345, "total": 1035}
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        response = barte_client.simulate_installments(amount=1000, brand="visa")
        
        assert response == mock_response
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
            "status": "succeeded"
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        refund_data = {"amount": 1000}
        response = barte_client.refund_charge("chr_123456789", refund_data)
        
        assert response == mock_response
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
    def test_get_charge(self, mock_get, barte_client, mock_response):
        """Test getting a specific charge"""
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        response = barte_client.get_charge("chr_123456789")
        
        assert response == mock_response
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789",
            headers=barte_client.headers
        )

    @patch('requests.get')
    def test_list_charges(self, mock_get, barte_client):
        """Test listing all charges"""
        mock_response = {
            "data": [
                {"id": "chr_1", "amount": 1000},
                {"id": "chr_2", "amount": 2000}
            ],
            "has_more": False
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        params = {"limit": 2, "starting_after": "chr_0"}
        response = barte_client.list_charges(params)
        
        assert response == mock_response
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            params=params
        )

    @patch('requests.post')
    def test_cancel_charge(self, mock_post, barte_client, mock_response):
        """Test canceling a charge"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        response = barte_client.cancel_charge("chr_123456789")
        
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/cancel",
            headers=barte_client.headers
        )

    @patch('requests.post')
    def test_charge_with_card_token(self, mock_post, barte_client, mock_response):
        """Test creating a charge with card token"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        data = {
            "amount": 1000,
            "description": "Test charge with token",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            },
            "installments": 1
        }

        response = barte_client.charge_with_card_token("tok_123456", data)
        
        expected_data = {
            **data,
            "payment_method": "credit_card",
            "card_token": "tok_123456"
        }
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data
        )

    @patch('requests.get')
    def test_get_pix_qrcode(self, mock_get, barte_client):
        """Test getting PIX QR code"""
        mock_response = {
            "qr_code": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000",
            "qr_code_image": "https://api.barte.com.br/v1/qrcodes/123456.png",
            "copy_and_paste": "00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426614174000"
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        response = barte_client.get_pix_qrcode("chr_123456789")
        
        assert response == mock_response
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/pix",
            headers=barte_client.headers
        )

    @patch('requests.post')
    def test_create_recurring_charge(self, mock_post, barte_client, mock_response):
        """Test creating a recurring charge"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        data = {
            "amount": 5990,
            "description": "Monthly Subscription",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            },
            "card_token": "tok_123456",
            "recurrence": {
                "interval": "month",
                "interval_count": 1
            }
        }

        response = barte_client.create_recurring_charge(data)
        
        expected_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "recurring": True
        }
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data
        )

    @patch('requests.post')
    def test_create_installment_charge_with_fee(self, mock_post, barte_client, mock_response):
        """Test creating an installment charge with customer fees"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        data = {
            "amount": 10000,
            "description": "Installment Purchase",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            },
            "card_token": "tok_123456",
            "installments": 3
        }

        response = barte_client.create_installment_charge_with_fee(data)
        
        expected_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "split_fee": True
        }
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data
        )

    @patch('requests.post')
    def test_create_installment_charge_no_fee(self, mock_post, barte_client, mock_response):
        """Test creating an installment charge without customer fees"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        data = {
            "amount": 10000,
            "description": "Installment Purchase",
            "customer": {
                "name": "John Doe",
                "tax_id": "123.456.789-00",
                "email": "john@example.com"
            },
            "card_token": "tok_123456",
            "installments": 3
        }

        response = barte_client.create_installment_charge_no_fee(data)
        
        expected_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "split_fee": False
        }
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges",
            headers=barte_client.headers,
            json=expected_data
        )

    @patch('requests.get')
    def test_get_charge_refunds(self, mock_get, barte_client):
        """Test getting charge refunds"""
        mock_response = {
            "data": [
                {
                    "id": "ref_1",
                    "charge_id": "chr_123456789",
                    "amount": 500,
                    "status": "succeeded"
                }
            ],
            "has_more": False
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        response = barte_client.get_charge_refunds("chr_123456789")
        
        assert response == mock_response
        mock_get.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/refunds",
            headers=barte_client.headers
        )

    @patch('requests.post')
    def test_refund_charge_without_data(self, mock_post, barte_client, mock_response):
        """Test refunding a charge without specifying amount"""
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = Mock()

        response = barte_client.refund_charge("chr_123456789")
        
        assert response == mock_response
        mock_post.assert_called_once_with(
            f"{barte_client.base_url}/v1/charges/chr_123456789/refund",
            headers=barte_client.headers,
            json={}
        ) 