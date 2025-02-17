from typing import Dict, Any, Optional, Union
from dataclasses import asdict
import requests
from dacite import from_dict
from .models import (
    Charge,
    CardToken,
    Refund,
    PixCharge,
    DACITE_CONFIG,
    Buyer,
    BuyerList,
    Order,
    ChargeList,
    OrderPayload,
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
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        BarteClient._instance = self

    @classmethod
    def get_instance(cls) -> "BarteClient":
        if cls._instance is None:
            raise RuntimeError(
                "BarteClient not initialized. Call BarteClient(api_key) first."
            )
        return cls._instance

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Private method to centralize HTTP requests.

        Args:
            method: HTTP method (e.g., 'GET', 'POST', 'DELETE', etc.)
            path: API endpoint path (e.g., '/v2/orders')
            params: Query parameters for GET requests.
            json: JSON body for POST, PATCH requests.

        Returns:
            The response JSON as a dictionary.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, params=params, json=json)
        response.raise_for_status()
        return response.json()

    def create_order(self, data: Union[Dict[str, Any], OrderPayload]) -> Order:
        """Create a new order"""
        if isinstance(data, OrderPayload):
            data = asdict(data)
        json_response = self._request("POST", "/v2/orders", json=data)
        return from_dict(data_class=Order, data=json_response, config=DACITE_CONFIG)

    def get_charge(self, charge_id: str) -> Charge:
        """Get a specific charge"""
        json_response = self._request("GET", f"/v2/charges/{charge_id}")
        return from_dict(data_class=Charge, data=json_response, config=DACITE_CONFIG)

    def list_charges(self, params: Optional[Dict[str, Any]] = None) -> ChargeList:
        """List all charges with optional filters"""
        json_response = self._request("GET", "/v2/charges", params=params)
        return from_dict(
            data_class=ChargeList, data=json_response, config=DACITE_CONFIG
        )

    def cancel_charge(self, charge_id: str) -> None:
        """Cancel a specific charge"""
        self._request("DELETE", f"/v2/charges/{charge_id}")

    def create_buyer(self, buyer_data: Dict[str, Any]) -> Buyer:
        """Create a buyer"""
        json_response = self._request("POST", "/v2/buyers", json=buyer_data)
        return from_dict(data_class=Buyer, data=json_response, config=DACITE_CONFIG)

    def get_buyer(self, filters: Dict[str, Any]) -> BuyerList:
        """Get buyers based on filters"""
        json_response = self._request("GET", "/v2/buyers", params=filters)
        return from_dict(data_class=BuyerList, data=json_response, config=DACITE_CONFIG)

    def create_card_token(self, card_data: Dict[str, Any]) -> CardToken:
        """Create a token for a credit card"""
        json_response = self._request("POST", "/v2/cards", json=card_data)
        return from_dict(data_class=CardToken, data=json_response, config=DACITE_CONFIG)

    def get_pix_qrcode(self, charge_id: str) -> PixCharge:
        """Get PIX QR Code data for a charge"""
        json_response = self._request("GET", f"/v2/charges/{charge_id}")
        return from_dict(data_class=PixCharge, data=json_response, config=DACITE_CONFIG)

    def refund_charge(self, charge_id: str, as_fraud: Optional[bool] = False) -> Refund:
        """Refund a charge"""
        json_response = self._request(
            "PATCH", f"/v2/charges/{charge_id}/refund", json={"asFraud": as_fraud}
        )
        return from_dict(data_class=Refund, data=json_response, config=DACITE_CONFIG)
