from typing import Dict, Any, Optional
import requests

class BarteClient:
    VALID_ENVIRONMENTS = ["production", "sandbox"]

    def __init__(self, api_key: str, environment: str = "production"):
        """
        Inicializa o cliente da API Barte
        
        Args:
            api_key: Chave de API fornecida pela Barte
            environment: Ambiente de execução ("production" ou "sandbox")
            
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

    def create_charge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new charge
        
        Args:
            data: Dictionary containing:
                - amount: Amount in cents (required)
                - currency: Currency code (default: BRL)
                - payment_method: Payment method (required)
                - description: Charge description
                - customer: Customer data (required)
                - metadata: Additional data
                - statement_descriptor: Text that will appear on the invoice
                - payment_settings: Payment specific configurations
                - antifraud_settings: Anti-fraud settings
                
        Returns:
            API response with charge data
        """
        endpoint = f"{self.base_url}/v1/charges"
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_charge(self, charge_id: str) -> Dict[str, Any]:
        """
        Obtém os dados de uma cobrança específica
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            Dados da cobrança
        """
        endpoint = f"{self.base_url}/v1/charges/{charge_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_charges(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todas as cobranças com filtros opcionais
        
        Args:
            params: Parâmetros de filtro (opcional)
            
        Returns:
            Lista de cobranças
        """
        endpoint = f"{self.base_url}/v1/charges"
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def cancel_charge(self, charge_id: str) -> Dict[str, Any]:
        """
        Cancela uma cobrança específica
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            Dados da cobrança cancelada
        """
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/cancel"
        response = requests.post(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_card_token(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a token for a credit card
        
        Args:
            card_data: Dictionary with card data containing:
                - number: Card number
                - holder_name: Cardholder name
                - expiration_month: Expiration month (1-12)
                - expiration_year: Expiration year (YYYY)
                - cvv: Security code
        
        Returns:
            API response with card token
        
        Example:
            card_data = {
                "number": "4111111111111111",
                "holder_name": "John Smith",
                "expiration_month": 12,
                "expiration_year": 2025,
                "cvv": "123"
            }
        """
        endpoint = f"{self.base_url}/v1/tokens"
        response = requests.post(endpoint, headers=self.headers, json=card_data)
        response.raise_for_status()
        return response.json()

    def charge_with_card_token(self, token_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma cobrança usando um token de cartão existente
        
        Args:
            token_id: ID do token do cartão previamente criado
            data: Dicionário com os dados da transação contendo:
                - amount: Valor em centavos
                - description: Descrição da cobrança
                - customer: Dados do cliente
                - installments: Número de parcelas (opcional)
                - capture: Se deve capturar automaticamente (opcional)
                - statement_descriptor: Descrição que aparecerá na fatura (opcional)
        
        Returns:
            Resposta da API com os dados da transação
        
        Example:
            data = {
                "amount": 1000,
                "description": "Compra com cartão tokenizado",
                "customer": {
                    "name": "João da Silva",
                    "tax_id": "123.456.789-00",
                    "email": "joao@exemplo.com"
                },
                "installments": 1,
                "capture": True
            }
        """
        endpoint = f"{self.base_url}/v1/charges"
        
        # Prepara os dados da transação incluindo o token
        transaction_data = {
            **data,
            "payment_method": "credit_card",
            "card_token": token_id
        }
        
        response = requests.post(endpoint, headers=self.headers, json=transaction_data)
        response.raise_for_status()
        return response.json()

    def create_pix_charge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a PIX charge
        
        Args:
            data: Dictionary with charge data containing:
                - amount: Amount in cents
                - description: Charge description
                - customer: Customer data
                - expiration_date: Expiration date (optional)
                
        Returns:
            API response with PIX charge data
        
        Example:
            data = {
                "amount": 1000,
                "description": "Order #123",
                "customer": {
                    "name": "John Smith",
                    "tax_id": "123.456.789-00",
                    "email": "john@example.com"
                },
                "expiration_date": "2024-12-31T23:59:59Z"
            }
        """
        endpoint = f"{self.base_url}/v1/charges"
        
        # Prepara os dados específicos para PIX
        pix_data = {
            **data,
            "payment_method": "pix"
        }
        
        response = requests.post(endpoint, headers=self.headers, json=pix_data)
        response.raise_for_status()
        return response.json()

    def get_pix_qrcode(self, charge_id: str) -> Dict[str, Any]:
        """
        Gets PIX QR Code data for a charge
        
        Args:
            charge_id: PIX charge ID
            
        Returns:
            QR Code data including:
                - qr_code: QR Code string
                - qr_code_image: QR Code image URL
                - copy_and_paste: PIX copy and paste code
        """
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/pix"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_recurring_charge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a recurring charge with credit card
        
        Args:
            data: Dictionary with charge data containing:
                - amount: Amount in cents
                - description: Charge description
                - customer: Customer data
                - card_token: Card token
                - recurrence: Recurrence data
                
        Returns:
            API response with recurring charge data
        
        Example:
            data = {
                "amount": 5990,
                "description": "Monthly Subscription",
                "customer": {
                    "name": "John Smith",
                    "tax_id": "123.456.789-00",
                    "email": "john@example.com"
                },
                "card_token": "tok_123456",
                "recurrence": {
                    "interval": "month",
                    "interval_count": 1
                }
            }
        """
        endpoint = f"{self.base_url}/v1/charges"
        
        charge_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "recurring": True
        }
        
        response = requests.post(endpoint, headers=self.headers, json=charge_data)
        response.raise_for_status()
        return response.json()

    def create_installment_charge_with_fee(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an installment charge with fees passed to customer
        
        Args:
            data: Dictionary with charge data containing:
                - amount: Amount in cents
                - description: Charge description
                - customer: Customer data
                - card_token: Card token
                - installments: Number of installments
                
        Returns:
            API response with installment charge data
        
        Example:
            data = {
                "amount": 10000,
                "description": "Installment Purchase",
                "customer": {
                    "name": "John Smith",
                    "tax_id": "123.456.789-00",
                    "email": "john@example.com"
                },
                "card_token": "tok_123456",
                "installments": 3
            }
        """
        endpoint = f"{self.base_url}/v1/charges"
        
        charge_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "split_fee": True  # Indica que as taxas serão repassadas ao cliente
        }
        
        response = requests.post(endpoint, headers=self.headers, json=charge_data)
        response.raise_for_status()
        return response.json()

    def create_installment_charge_no_fee(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an installment charge with merchant assuming the fees
        
        Args:
            data: Dictionary with charge data containing:
                - amount: Amount in cents
                - description: Charge description
                - customer: Customer data
                - card_token: Card token
                - installments: Number of installments
                
        Returns:
            API response with installment charge data
        
        Example:
            data = {
                "amount": 10000,
                "description": "Installment Purchase",
                "customer": {
                    "name": "John Smith",
                    "tax_id": "123.456.789-00",
                    "email": "john@example.com"
                },
                "card_token": "tok_123456",
                "installments": 3
            }
        """
        endpoint = f"{self.base_url}/v1/charges"
        
        charge_data = {
            **data,
            "payment_method": "credit_card",
            "capture": True,
            "split_fee": False  # Indica que as taxas NÃO serão repassadas ao cliente
        }
        
        response = requests.post(endpoint, headers=self.headers, json=charge_data)
        response.raise_for_status()
        return response.json()

    def simulate_installments(self, amount: int, brand: str) -> Dict[str, Any]:
        """
        Simulates credit card installments
        
        Args:
            amount: Amount in cents
            brand: Card brand (visa, mastercard, etc)
            
        Returns:
            Installment simulation data
        """
        endpoint = f"{self.base_url}/v1/simulate/installments"
        params = {"amount": amount, "brand": brand}
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_charge_refunds(self, charge_id: str) -> Dict[str, Any]:
        """
        Gets all refunds for a charge
        
        Args:
            charge_id: Charge ID
            
        Returns:
            List of refunds
        """
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/refunds"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def refund_charge(self, charge_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refunds a charge
        
        Args:
            charge_id: Charge ID
            data: Refund data (optional)
                - amount: Amount to refund (if partial refund)
                - metadata: Additional data
                
        Returns:
            Refund data
        """
        endpoint = f"{self.base_url}/v1/charges/{charge_id}/refund"
        response = requests.post(endpoint, headers=self.headers, json=data or {})
        response.raise_for_status()
        return response.json() 