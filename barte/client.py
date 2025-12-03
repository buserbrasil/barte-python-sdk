from dataclasses import asdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

import requests
from dacite import from_dict

from barte.__version__ import __version__

from .models import (
    DACITE_CONFIG,
    Buyer,
    BuyerCard,
    BuyerList,
    CardToken,
    Charge,
    ChargeList,
    ErrorResponse,
    InstallmentOption,
    Order,
    OrderPayload,
    PartialRefund,
    PixCharge,
    Refund,
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
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Token-Api": api_key,
                "Content-Type": "application/json",
                "User-Agent": f"barte-client/python version={__version__}",
            }
        )
        BarteClient._instance = self

    @classmethod
    def get_instance(cls) -> "BarteClient":
        if cls._instance is None:
            raise RuntimeError(
                "BarteClient not initialized. Call BarteClient(api_key) first."
            )
        return cls._instance

    def _extract_error_data(
        self, json_response: Union[Dict[str, Any], List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """Extract error data from API response if present."""
        if isinstance(json_response, dict) and "errors" in json_response:
            return json_response

        if isinstance(json_response, list) and json_response:
            first_item = json_response[0]
            if isinstance(first_item, dict) and "errors" in first_item:
                return first_item

        return None

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Any], None]:
        """
        Private method to centralize HTTP requests.

        Args:
            method: HTTP method (e.g., 'GET', 'POST', 'DELETE', etc.)
            path: API endpoint path (e.g., '/v2/orders')
            params: Query parameters for GET requests.
            json: JSON body for POST, PATCH requests.

        Returns:
            The response JSON as a dictionary or list.

        Raises:
            BarteError: If the API returns an error response with Barte error codes.
            HTTPError: If the HTTP request returned an unsuccessful status code
                       without a structured error response.
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, params=params, json=json)

        if response.status_code == 204:
            return None

        try:
            json_response = response.json()
        except ValueError:
            response.raise_for_status()
            return None

        if error_data := self._extract_error_data(json_response):
            error_response = from_dict(
                data_class=ErrorResponse, data=error_data, config=DACITE_CONFIG
            )
            error_response.raise_exception(response=response)

        response.raise_for_status()

        return json_response

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

    def get_order(self, order_id: str) -> Order:
        """Get a specific order"""
        json_response = self._request("GET", f"/v2/orders/{order_id}")
        return from_dict(data_class=Order, data=json_response, config=DACITE_CONFIG)

    def list_charges(self, params: Optional[Dict[str, Any]] = None) -> ChargeList:
        """List all charges with optional filters"""
        json_response = self._request("GET", "/v2/charges", params=params)
        return from_dict(
            data_class=ChargeList, data=json_response, config=DACITE_CONFIG
        )

    def cancel_charge(self, charge_id: str) -> None:
        """Cancel a specific charge"""
        self._request("DELETE", f"/v2/charges/{charge_id}")

    def create_buyer(self, buyer_data: Dict[str, Any], version: str = "v2") -> Buyer:
        """Create a buyer"""
        json_response = self._request("POST", f"/{version}/buyers", json=buyer_data)
        return from_dict(data_class=Buyer, data=json_response, config=DACITE_CONFIG)

    def get_buyer(self, filters: Dict[str, Any]) -> BuyerList:
        """Get buyers based on filters"""
        json_response = self._request("GET", "/v2/buyers", params=filters)
        return from_dict(data_class=BuyerList, data=json_response, config=DACITE_CONFIG)

    def update_buyer(self, uuid: str, buyer_data: Dict[str, Any]) -> None:
        """Get buyers based on filters"""
        self._request("PUT", f"/v2/buyers/{uuid}", json=buyer_data)

    def create_card_token(self, card_data: Dict[str, Any]) -> CardToken:
        """Create a token for a credit card"""
        json_response = self._request("POST", "/v2/cards", json=card_data)
        return from_dict(data_class=CardToken, data=json_response, config=DACITE_CONFIG)

    def get_buyer_cards(self, buyer_id: str) -> List[BuyerCard]:
        """Create a token for a credit card"""
        json_response = self._request("GET", f"/payment/v1/cards/{buyer_id}")
        return [
            from_dict(data_class=BuyerCard, data=item, config=DACITE_CONFIG)
            for item in json_response
        ]

    def get_pix_qrcode(self, charge_id: str) -> PixCharge:
        """Get PIX QR Code data for a charge"""
        json_response = self._request("GET", f"/v2/charges/{charge_id}")
        return from_dict(data_class=PixCharge, data=json_response, config=DACITE_CONFIG)

    def refund_charge(self, charge_id: str, as_fraud: Optional[bool] = False) -> Charge:
        """Refund a charge

        Raises:
            BarteError: When the API returns an error response with Barte error codes.
        """
        json_response = self._request(
            "PATCH", f"/v2/charges/{charge_id}/refund", json={"asFraud": as_fraud}
        )
        return from_dict(data_class=Charge, data=json_response, config=DACITE_CONFIG)

    def partial_refund_charge(
        self, charge_id: str, value: Decimal
    ) -> List[PartialRefund]:
        """Refund a charge partialy

        Raises:
            BarteError: When the API returns an error response with Barte error codes.
        """
        json_response = self._request(
            "PATCH", f"/v2/charges/partial-refund/{charge_id}", json={"value": value}
        )
        return [
            from_dict(data_class=PartialRefund, data=item, config=DACITE_CONFIG)
            for item in json_response
        ]

    def get_refund(self, charge_id: str) -> List[Refund]:
        """Get refund detail"""
        json_response = self._request("GET", f"/v2/charges/partial-refund/{charge_id}")
        return [
            from_dict(data_class=Refund, data=item, config=DACITE_CONFIG)
            for item in json_response
        ]

    def get_installments(
        self, amount: Decimal, max_installments: int
    ) -> List[InstallmentOption]:
        """Get a list of installments value"""
        json_response = self._request(
            "GET",
            "/v2/orders/installments-payment",
            params={"amount": amount, "maxInstallments": max_installments},
        )
        return [
            from_dict(data_class=InstallmentOption, data=item) for item in json_response
        ]
