import random
import pytest
import os
import datetime

from barte import BarteClient

# Skip these tests if no API key is provided
pytestmark = pytest.mark.skipif(
    not os.getenv("BARTE_API_KEY"), reason="No API key provided for integration tests"
)


def generate_document_number():
    digits = [random.randint(0, 9) for _ in range(9)]
    total = sum((10 - i) * digits[i] for i in range(9))
    remainder = total % 11
    digits.append(0 if remainder < 2 else 11 - remainder)

    total = sum((11 - i) * digits[i] for i in range(10))
    remainder = total % 11
    digits.append(0 if remainder < 2 else 11 - remainder)
    return "".join(str(digit) for digit in digits)


@pytest.fixture
def client():
    return BarteClient(api_key=os.getenv("BARTE_API_KEY"), environment="sandbox")


@pytest.fixture
def buyer_data():
    doc_number = generate_document_number()
    return {
        "document": {
            "documentNumber": doc_number,
            "documentType": "cpf",
            "documentNation": "BR",
        },
        "name": "ClienteExterno-sTZ4",
        "email": "ClienteExterno-sTZ4@email.com",
        "countryCode": "+55",
        "phone": "11999999999",
        "alternativeEmail": "",
        "address": {
            "zipCode": "01310-200",
            "street": "Avenida Paulista",
            "number": "620",
            "complement": "",
            "district": "Bela Vista",
            "city": "São Paulo",
            "state": "SP",
            "country": "BR",
        },
    }


@pytest.fixture
def payment_template(buyer_data):
    return {
        "method": "CREDIT_CARD_EARLY_SELLER",
        "card": {"cardToken": None},
        "brand": "mastercard",
        "fraudData": {
            "internationalDocument": {
                "documentNumber": buyer_data["document"]["documentNumber"],
                "documentType": "CPF",
                "documentNation": "BR",
            },
            "name": buyer_data["name"],
            "email": buyer_data["email"],
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
    }


class TestBarteIntegration:
    def test_create_order_and_fetch_charge(self, client, buyer_data, payment_template):
        buyer = client.create_buyer(buyer_data)

        assert buyer.uuid
        assert buyer.document == buyer_data["document"]["documentNumber"]

        card_token = client.create_card_token(
            {
                "holderName": "JOSE DAS NEVES TEST",
                "number": "5383638854440891",
                "cvv": "220",
                "expiration": "12/2025",
                "buyerUuid": buyer.uuid,
            }
        )
        assert card_token.uuid
        assert card_token.last4digits == "0891"

        payment_template["card"]["cardToken"] = card_token.uuid

        order_data = {
            "startDate": datetime.date.today().strftime("%Y-%m-%d"),
            "value": 60,
            "installments": 1,
            "title": "Order 1",
            "attemptReference": "349cea7a-6a52-4edd-9c73-7773a75bf05d",
            "description": "Order description",
            "payment": payment_template,
            "uuidBuyer": buyer.uuid,
        }

        order = client.create_order(order_data)

        assert order.uuid
        assert len(order.charges) == 1

        charge = client.get_charge(order.charges[0].uuid)
        assert charge.uuid == order.charges[0].uuid

    def test_get_installments(self, client):
        installments = client.get_installments(amount=200, max_installments=4)
        assert len(installments) == 4
        assert installments[0].totalAmount == 200
