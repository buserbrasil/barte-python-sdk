from typing import Dict, Any, Optional, List
import requests
from dacite import from_dict
from .models import (
    Charge,
    CardToken,
    Refund,
    InstallmentOptions,
    PixCharge,
    DACITE_CONFIG,
    Config,
    InstallmentSimulation,
    Buyer,
    BuyerList,
    Order,
)


class BarteClient:
    VALID_ENVIRONMENTS = ["production", "sandbox"]
    _instance = None

    def __init__(self, api_key: str, environment: str = "production"):
        """
        Initialize the Barte API client

        Args:
            api_key: API key provided by Barte
            environment: Environment ("production" or "sandbox")

        Raises:
            ValueError: If the environment is not "production" or "sandbox"
        """
        if environment not in self.VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment. Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}"
            )

        self.api_key = api_key
        self.base_url = (
            "https://api.barte.com"
            if environment == "production"
            else "https://sandbox-api.barte.com"
        )
        self.headers = {"X-Token-Api": api_key, "Content-Type": "application/json"}
        BarteClient._instance = self

    @classmethod
    def get_instance(cls) -> "BarteClient":
        if cls._instance is None:
            raise RuntimeError(
                "BarteClient not initialized. Call BarteClient(api_key) first."
            )
        return cls._instance

    def create_order(self, data: Dict[str, Any]) -> Order:
        """Create a new order"""
        endpoint = f"{self.base_url}/v2/orders"
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return from_dict(data_class=Order, data=response.json(), config=DACITE_CONFIG)

    def get_charge(self, charge_id: str) -> Charge:
        """Get a specific charge"""
        endpoint = f"{self.base_url}/v2/charges/{charge_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def list_charges(self, params: Optional[Dict[str, Any]] = None) -> List[Charge]:
        """List all charges with optional filters"""
        endpoint = f"{self.base_url}/v1/charges"
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return [
            from_dict(data_class=Charge, data=item, config=DACITE_CONFIG)
            for item in response.json()["data"]
        ]

    def cancel_charge(self, charge_id: str) -> None:
        """Cancel a specific charge"""
        endpoint = f"{self.base_url}/v2/charges/{charge_id}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()

    def create_buyer(self, buyer_data: Dict[str, any]) -> Buyer:
        endpoint = f"{self.base_url}/v2/buyers"
        response = requests.post(endpoint, headers=self.headers, json=buyer_data)
        response.raise_for_status()
        return from_dict(data_class=Buyer, data=response.json(), config=DACITE_CONFIG)

    def get_buyer(self, filters: Dict[str, any]) -> BuyerList:
        endpoint = f"{self.base_url}/v2/buyers"
        response = requests.get(endpoint, params=filters, headers=self.headers)
        response.raise_for_status()
        return from_dict(
            data_class=BuyerList, data=response.json(), config=DACITE_CONFIG
        )

    def create_card_token(self, card_data: Dict[str, Any]) -> CardToken:
        """Create a token for a credit card"""
        endpoint = f"{self.base_url}/v2/cards"
        response = requests.post(endpoint, headers=self.headers, json=card_data)
        response.raise_for_status()
        return from_dict(
            data_class=CardToken, data=response.json(), config=DACITE_CONFIG
        )

    def charge_with_card_token(self, token_id: str, data: Dict[str, Any]) -> Charge:
        """Create a charge using an existing card token"""
        endpoint = f"{self.base_url}/v1/charges"

        transaction_data = {
            **data,
            "payment_method": "credit_card",
            "card_token": token_id,
        }

        response = requests.post(endpoint, headers=self.headers, json=transaction_data)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def create_pix_charge(self, data: Dict[str, Any]) -> PixCharge:
        """Create a PIX charge"""
        endpoint = f"{self.base_url}/v1/charges"

        pix_data = {**data, "payment_method": "pix"}

        response = requests.post(endpoint, headers=self.headers, json=pix_data)
        response.raise_for_status()
        return from_dict(
            data_class=PixCharge, data=response.json(), config=DACITE_CONFIG
        )

    def get_pix_qrcode(self, charge_id: str) -> PixCharge:
        """Get PIX QR Code data for a charge"""
        endpoint = f"{self.base_url}/v2/charges/{charge_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return from_dict(
            data_class=PixCharge, data=response.json(), config=DACITE_CONFIG
        )

    def simulate_installments(self, amount: int, brand: str) -> InstallmentOptions:
        """Simulate credit card installments"""
        endpoint = f"{self.base_url}/v1/simulate/installments"
        params = {"amount": amount, "brand": brand}
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return from_dict(
            data_class=InstallmentOptions,
            data=response.json(),
            config=Config(cast=[List[InstallmentSimulation]]),
        )

    def refund_charge(self, charge_id: str, as_fraud: Optional[bool] = False) -> Refund:
        """Refund a charge"""
        endpoint = f"{self.base_url}/v2/charges/{charge_id}/refund"
        response = requests.patch(
            endpoint, headers=self.headers, json={"asFraud": as_fraud}
        )
        response.raise_for_status()
        return from_dict(data_class=Refund, data=response.json(), config=DACITE_CONFIG)
