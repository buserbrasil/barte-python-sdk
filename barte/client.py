from typing import Dict, Any, Optional, List
import requests
from dacite import from_dict
from .models import (
    Charge, CardToken, Refund, InstallmentOptions,
    PixCharge, PixQRCode, DACITE_CONFIG, Config,
    InstallmentSimulation
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
            raise ValueError(f"Invalid environment. Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}")
            
        self.api_key = api_key
        self.base_url = "https://api.barte.com.br" if environment == "production" else "https://sandbox-api.barte.com.br"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        BarteClient._instance = self

    @classmethod
    def get_instance(cls) -> "BarteClient":
        if cls._instance is None:
            raise RuntimeError("BarteClient not initialized. Call BarteClient(api_key) first.")
        return cls._instance

    def create_charge(self, data: Dict[str, Any]) -> Charge:
        """Create a new charge"""
        endpoint = f"{self.base_url}/v1/charges"
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def get_charge(self, charge_id: str) -> Charge:
        """Get a specific charge"""
        endpoint = f"{self.base_url}/v1/charges/{charge_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def list_charges(self, params: Optional[Dict[str, Any]] = None) -> List[Charge]:
        """List all charges with optional filters"""
        endpoint = f"{self.base_url}/v1/charges"
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return [from_dict(data_class=Charge, data=item, config=DACITE_CONFIG) for item in response.json()["data"]]

    def cancel_charge(self, charge_id: str) -> Charge:
        """Cancel a specific charge"""
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/cancel"
        response = requests.post(endpoint, headers=self.headers)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def create_card_token(self, card_data: Dict[str, Any]) -> CardToken:
        """Create a token for a credit card"""
        endpoint = f"{self.base_url}/v1/tokens"
        response = requests.post(endpoint, headers=self.headers, json=card_data)
        response.raise_for_status()
        return from_dict(data_class=CardToken, data=response.json(), config=DACITE_CONFIG)

    def charge_with_card_token(self, token_id: str, data: Dict[str, Any]) -> Charge:
        """Create a charge using an existing card token"""
        endpoint = f"{self.base_url}/v1/charges"
        
        transaction_data = {
            **data,
            "payment_method": "credit_card",
            "card_token": token_id
        }
        
        response = requests.post(endpoint, headers=self.headers, json=transaction_data)
        response.raise_for_status()
        return from_dict(data_class=Charge, data=response.json(), config=DACITE_CONFIG)

    def create_pix_charge(self, data: Dict[str, Any]) -> PixCharge:
        """Create a PIX charge"""
        endpoint = f"{self.base_url}/v1/charges"
        
        pix_data = {
            **data,
            "payment_method": "pix"
        }
        
        response = requests.post(endpoint, headers=self.headers, json=pix_data)
        response.raise_for_status()
        return from_dict(data_class=PixCharge, data=response.json(), config=DACITE_CONFIG)

    def get_pix_qrcode(self, charge_id: str) -> PixQRCode:
        """Get PIX QR Code data for a charge"""
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/pix"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return from_dict(data_class=PixQRCode, data=response.json())

    def simulate_installments(self, amount: int, brand: str) -> InstallmentOptions:
        """Simulate credit card installments"""
        endpoint = f"{self.base_url}/v1/simulate/installments"
        params = {"amount": amount, "brand": brand}
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return from_dict(
            data_class=InstallmentOptions,
            data=response.json(),
            config=Config(cast=[List[InstallmentSimulation]])
        )

    def get_charge_refunds(self, charge_id: str) -> List[Refund]:
        """Get all refunds for a charge"""
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/refunds"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return [from_dict(data_class=Refund, data=item, config=DACITE_CONFIG) for item in response.json()["data"]]

    def refund_charge(self, charge_id: str, data: Optional[Dict[str, Any]] = None) -> Refund:
        """Refund a charge"""
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/refund"
        response = requests.post(endpoint, headers=self.headers, json=data or {})
        response.raise_for_status()
        return from_dict(data_class=Refund, data=response.json(), config=DACITE_CONFIG) 