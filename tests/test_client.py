import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from dacite import from_dict
from barte import BarteClient, Charge, CardToken, Refund, PixCharge
from barte.models import DACITE_CONFIG, Order, InstallmentOption


@pytest.fixture
def barte_client():
    client = BarteClient(api_key="test_key", environment="sandbox")
    BarteClient._instance = client  # For model instance methods
    return client


@pytest.fixture
def mock_order_response():
    return {
        "uuid": "e51e67b3-8dda-4bf9-ab1b-5d5504439bfd",
        "status": "PAID",
        "title": "Barte - Postman - h6C",
        "description": "Barte - Postman - oZ2",
        "value": 60,
        "installments": 1,
        "startDate": "2025-02-07",
        "payment": "CREDIT_CARD_EARLY_SELLER",
        "customer": {
            "document": "19340911032",
            "type": "CPF",
            "documentCountry": "BR",
            "name": "John Doe",
            "email": "johndoe@email.com",
            "phone": "11999999999",
            "alternativeEmail": "",
        },
        "idempotencyKey": "349cea7a-6a52-4edd-9c73-7773a75bf05d",
        "charges": [
            {
                "uuid": "35b45f90-11bc-448a-bcb4-969a9697d4d5",
                "title": "Barte - Postman - h6C",
                "expirationDate": "2025-02-07",
                "paidDate": "2025-02-07",
                "value": 60.00,
                "paymentMethod": "CREDIT_CARD_EARLY_SELLER",
                "status": "PAID",
                "customer": {
                    "document": "19340911032",
                    "type": "CPF",
                    "name": "John Doe",
                    "email": "ClienteExterno-sTZ4@email.com",
                    "phone": "11999999999",
                    "alternativeEmail": "",
                },
                "authorizationCode": "8343333",
                "authorizationNsu": "4851680",
            }
        ],
    }


@pytest.fixture
def mock_charge_response():
    return {
        "uuid": "8b6b2ddc-7ccb-4d1f-8832-ef0adc62ed31",
        "title": "Barte - Postman - ySw",
        "expirationDate": "2025-02-12",
        "paidDate": "2025-02-12",
        "value": 1000.00,
        "paymentMethod": "CREDIT_CARD_EARLY_SELLER",
        "status": "PAID",
        "customer": {
            "uuid": "",
            "document": "19340911032",
            "type": "CPF",
            "name": "John Doe",
            "email": "ClienteExterno-sTZ4@email.com",
            "phone": "11999999999",
            "alternativeEmail": "",
        },
        "authorizationCode": "4135497",
        "authorizationNsu": "5805245",
    }


@pytest.fixture
def mock_pix_charge_response():
    return {
        "uuid": "7a384917-e73e-466e-b90d-8c9f04e7fa9f",
        "title": "Teste",
        "expirationDate": "2025-02-12",
        "value": 3.00,
        "paymentMethod": "PIX",
        "status": "SCHEDULED",
        "customer": {
            "uuid": "",
            "document": "19340911032",
            "type": "CPF",
            "name": "John Doe",
            "email": "ClienteExterno-sTZ4@email.com",
            "phone": "11999999999",
            "alternativeEmail": "",
        },
        "pixCode": (
            "000201010211261230014BR.GOV.BCB.PIX01000297BENEFICIÁRIO FINAL: "
            "BUSER BRASIL TECNOLOGIA LTDA \n Intermediado pela plataforma Barte Brasil Ltda"
            "52040000530398654040.035802BR5920ClienteExterno-sTZ4 600062360532cd5e99706300441787ee6188e4814fa263040CB9"
        ),
        "pixQRCodeImage": (
            "https://s3.amazonaws.com/sandbox-charge-docs.barte.corp/pix/"
            "155e846a-c237-43a3-95a9-b8c88b5d5833.png"
        ),
    }


@pytest.fixture
def mock_list_response():
    return {
        "content": [],
        "pageable": {
            "sort": {"unsorted": True, "sorted": False, "empty": True},
            "pageNumber": 0,
            "pageSize": 20,
            "offset": 0,
            "paged": True,
            "unpaged": False,
        },
        "totalElements": 1,
        "totalPages": 1,
        "last": False,
        "numberOfElements": 20,
        "size": 20,
        "number": 0,
        "sort": {"unsorted": True, "sorted": False, "empty": True},
        "first": True,
        "empty": False,
    }


@pytest.fixture
def mock_installments_reponse():
    return [
        {"installments": 1, "installmentAmount": 200.00, "totalAmount": 200.00},
        {"installments": 2, "installmentAmount": 107.30, "totalAmount": 214.60},
        {"installments": 3, "installmentAmount": 72.20, "totalAmount": 216.60},
        {"installments": 4, "installmentAmount": 54.50, "totalAmount": 218.00},
    ]


@pytest.fixture
def mock_buyer():
    return {
        "uuid": "fdfc8dd7-920e-42f1-9015-24e55fb37c6b",
        "document": "54120712605",
        "name": "John Doe",
        "email": "johndoe@email.com",
        "phone": "11999999999",
        "countryCode": "+55",
        "alternativeEmail": "",
    }


@pytest.fixture
def mock_buyer_cards_reponse():
    return [
        {
            "uuid": "2104da5d-376d-4fc8-bf70-dc91de9ce4b1",
            "status": "ACTIVE",
            "createdAt": "2025-02-23",
            "brand": "mastercard",
            "first6digits": "538363",
            "last4digits": "0891",
            "buyerId": "fdfc8dd7-920e-42f1-9015-24e55fb37c6b",
            "expirationMonth": "12",
            "expirationYear": "2025",
            "cardId": "031c4b4d-5e6b-43f3-bc14-aa8388e5f612",
        },
        {
            "uuid": "ad5ed29a-a174-4ba6-b86e-e2107cec14ba",
            "status": "ACTIVE",
            "createdAt": "2025-02-24",
            "brand": "mastercard",
            "first6digits": "538363",
            "last4digits": "0891",
            "buyerId": "fdfc8dd7-920e-42f1-9015-24e55fb37c6b",
            "expirationMonth": "12",
            "expirationYear": "2025",
            "cardId": "2830f415-993b-4dda-baa8-61d7a9452a3d",
        },
        {
            "uuid": "b0d1a3a4-7041-46cc-b02c-514c0ed31c70",
            "status": "ACTIVE",
            "createdAt": "2025-02-24",
            "brand": "mastercard",
            "first6digits": "538363",
            "last4digits": "0891",
            "buyerId": "fdfc8dd7-920e-42f1-9015-24e55fb37c6b",
            "expirationMonth": "12",
            "expirationYear": "2025",
            "cardId": "5f68a932-11a4-4f21-bdca-1788593c3264",
        },
    ]


class TestBarteClient:
    @patch("barte.client.requests.Session.request")
    def test_request_get(self, mock_request, barte_client):
        """Test _request method with GET (no JSON data)"""
        response_dict = {"key": "value"}
        # Configure the mock response:
        mock_request.return_value.json.return_value = response_dict
        mock_request.return_value.raise_for_status = Mock()

        result = barte_client._request("GET", "/test_endpoint")
        assert result == response_dict

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/test_endpoint",
            params=None,
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_request_post(self, mock_request, barte_client):
        """Test _request method with POST (with JSON data)"""
        request_dict = {"data": "value"}
        response_dict = {"key": "value"}
        mock_request.return_value.json.return_value = response_dict
        mock_request.return_value.raise_for_status = Mock()

        result = barte_client._request("POST", "/test_endpoint", json=request_dict)
        assert result == response_dict

        mock_request.assert_called_once_with(
            "POST",
            f"{barte_client.base_url}/test_endpoint",
            params=None,
            json=request_dict,
        )

    @patch("barte.client.requests.Session.request")
    def test_create_order(self, mock_request, barte_client, mock_order_response):
        """Test creating a new order using create_order"""
        mock_request.return_value.json.return_value = mock_order_response
        mock_request.return_value.raise_for_status = Mock()

        order_data = {
            "startDate": "2025-02-07",
            "value": 60,
            "installments": 1,
            "title": "Barte - Postman - h6C",
            "attemptReference": "349cea7a-6a52-4edd-9c73-7773a75bf05d",
            "description": "Barte - Postman - oZ2",
            "payment": {
                "method": "CREDIT_CARD_EARLY_SELLER",
                "card": {"cardToken": "790e8637-c16b-4ed5-a9bf-faec76dbc5aa"},
                "brand": "mastercard",
                "fraudData": {
                    "internationalDocument": {
                        "documentNumber": "19340911032",
                        "documentType": "CPF",
                        "documentNation": "BR",
                    },
                    "name": "John Doe",
                    "email": "ClienteExterno-sTZ4@email.com",
                    "phone": "1199999-9999",
                    "billingAddress": {
                        "country": "BR",
                        "state": "SP",
                        "city": "São Paulo",
                        "district": "Bela Vista",
                        "street": "Avenida Paulista",
                        "zipCode": "01310200",
                        "number": "620",
                        "complement": "",
                    },
                },
            },
            "uuidBuyer": "5929a30b-e68f-4c81-9481-d25adbabafeb",
        }
        order = barte_client.create_order(order_data)

        # Verify the returned object (converted to Order)
        assert isinstance(order, Order)
        assert order.value == 60
        assert order.customer.name == "John Doe"
        assert order.charges[0].uuid == "35b45f90-11bc-448a-bcb4-969a9697d4d5"
        assert isinstance(order.startDate, datetime)

        mock_request.assert_called_once_with(
            "POST",
            f"{barte_client.base_url}/v2/orders",
            params=None,
            json=order_data,
        )

    @patch("barte.client.requests.Session.request")
    def test_create_card_token(self, mock_request, barte_client):
        """Test creating a card token using create_card_token"""
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
        mock_request.return_value.json.return_value = mock_response
        mock_request.return_value.raise_for_status = Mock()

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

        mock_request.assert_called_once_with(
            "POST",
            f"{barte_client.base_url}/v2/cards",
            params=None,
            json=card_data,
        )

    @patch("barte.client.requests.Session.request")
    def test_refund_charge(self, mock_request, barte_client):
        """Test refunding a charge using refund_charge"""
        mock_response = {
            "uuid": "d54f6553-8bcf-4376-a995-aaffb6d29492",
            "title": "Barte - Postman - BgN",
            "expirationDate": "2025-02-12",
            "paidDate": "2025-02-12",
            "value": 23.00,
            "paymentMethod": "CREDIT_CARD_EARLY_SELLER",
            "status": "REFUND",
            "customer": {
                "uuid": "",
                "document": "19340911032",
                "type": "CPF",
                "name": "ClienteExterno-sTZ4 ",
                "email": "ClienteExterno-sTZ4@email.com",
                "phone": "11999999999",
                "alternativeEmail": "",
            },
            "authorizationCode": "3235588",
            "authorizationNsu": "5555742",
        }
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = Mock()
        mock_request.return_value = mock_response_obj

        refund = barte_client.refund_charge(
            "d54f6553-8bcf-4376-a995-aaffb6d29492", as_fraud=False
        )
        assert isinstance(refund, Refund)
        assert refund.uuid == "d54f6553-8bcf-4376-a995-aaffb6d29492"
        assert refund.value == 23.00
        assert refund.status == "REFUND"
        assert isinstance(refund.paidDate, datetime)

        mock_request.assert_called_once_with(
            "PATCH",
            f"{barte_client.base_url}/v2/charges/d54f6553-8bcf-4376-a995-aaffb6d29492/refund",
            params=None,
            json={"asFraud": False},
        )

    @patch("barte.client.requests.Session.request")
    def test_get_charge(self, mock_request, barte_client, mock_charge_response):
        """Test getting a specific charge using get_charge"""
        mock_request.return_value.json.return_value = mock_charge_response
        mock_request.return_value.raise_for_status = Mock()

        charge = barte_client.get_charge("8b6b2ddc-7ccb-4d1f-8832-ef0adc62ed31")
        assert isinstance(charge, Charge)
        assert charge.uuid == "8b6b2ddc-7ccb-4d1f-8832-ef0adc62ed31"
        assert charge.value == 1000.00
        assert charge.customer.name == "John Doe"
        assert isinstance(charge.paidDate, datetime)

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/v2/charges/8b6b2ddc-7ccb-4d1f-8832-ef0adc62ed31",
            params=None,
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_list_charges(
        self, mock_request, barte_client, mock_charge_response, mock_list_response
    ):
        """Test listing all charges using list_charges"""
        combined_response = {
            **mock_list_response,
            "content": [mock_charge_response],
            "has_more": False,
        }
        mock_request.return_value.json.return_value = combined_response
        mock_request.return_value.raise_for_status = Mock()

        params = {"customerDocument": "19340911032"}
        result = barte_client.list_charges(params)
        content = result.content
        assert len(content) == 1
        assert all(isinstance(c, Charge) for c in content)
        assert content[0].uuid == "8b6b2ddc-7ccb-4d1f-8832-ef0adc62ed31"
        assert all(isinstance(c.paidDate, datetime) for c in content)

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/v2/charges",
            params=params,
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_pix_charge_get_qrcode(
        self, mock_request, barte_client, mock_pix_charge_response
    ):
        """Test PIX charge QR code method using get_qr_code"""
        # For get_qr_code, the client calls its _request to fetch updated charge info.
        # Set the response and ensure a 200 status.
        mock_request.return_value.json.return_value = mock_pix_charge_response
        mock_request.return_value.raise_for_status = Mock()
        mock_request.return_value.status_code = 200

        pix_charge = from_dict(
            data_class=PixCharge,
            data=mock_pix_charge_response.copy(),
            config=DACITE_CONFIG,
        )
        qr_data = pix_charge.get_qr_code()

        assert qr_data.qr_code == pix_charge.pixCode
        assert qr_data.qr_code_image == pix_charge.pixQRCodeImage

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/v2/charges/{pix_charge.uuid}",
            params=None,
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_get_installments(
        self, mock_request, barte_client, mock_installments_reponse
    ):
        """Test getting a specific charge using get_charge"""
        mock_request.return_value.json.return_value = mock_installments_reponse
        mock_request.return_value.raise_for_status = Mock()

        amount = 200
        max_installments = 4

        installments = barte_client.get_installments(amount, max_installments)
        assert len(installments) == 4
        assert installments[0].installmentAmount == 200
        assert isinstance(installments[0], InstallmentOption)

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/v2/orders/installments-payment",
            params={"amount": amount, "maxInstallments": max_installments},
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_get_buyer_cards(
        self, mock_request, barte_client, mock_buyer_cards_reponse, mock_buyer
    ):
        """Test getting list of buyer cards"""
        mock_request.return_value.json.return_value = mock_buyer_cards_reponse
        mock_request.return_value.raise_for_status = Mock()

        card_list = barte_client.get_buyer_cards(mock_buyer["uuid"])
        assert len(card_list) == 3
        assert card_list[0].uuid == mock_buyer_cards_reponse[0]["uuid"]
        assert card_list[0].buyerId == mock_buyer["uuid"]

        mock_request.assert_called_once_with(
            "GET",
            f"{barte_client.base_url}/payment/v1/cards/{mock_buyer['uuid']}",
            params=None,
            json=None,
        )

    @patch("barte.client.requests.Session.request")
    def test_update_buyer(self, mock_request, barte_client, mock_buyer):
        """Test update buyer data"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        buyer_uuid = mock_buyer["uuid"]
        buyer_data = {
            "name": "New Name",
            "email": "newemail@mail.com",
            "phone": "99988882222",
            "alternativeEmail": "",
        }

        result = barte_client.update_buyer(buyer_uuid, buyer_data)

        assert result is None

        mock_request.assert_called_once_with(
            "PUT",
            f"{barte_client.base_url}/v2/buyers/{buyer_uuid}",
            params=None,
            json=buyer_data,
        )

    def test_client_singleton(self):
        """Test client singleton pattern"""
        # Reset singleton for initial state
        BarteClient._instance = None

        with pytest.raises(RuntimeError) as exc_info:
            BarteClient.get_instance()
        assert "BarteClient not initialized" in str(exc_info.value)

        client1 = BarteClient(api_key="test_key", environment="sandbox")
        assert BarteClient.get_instance() == client1

        client2 = BarteClient(api_key="another_key", environment="sandbox")
        assert BarteClient.get_instance() == client2
        assert client2.api_key == "another_key"

        # Reset singleton for other tests
        BarteClient._instance = None
