from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class Customer:
    name: str
    tax_id: str
    email: str

@dataclass
class CardToken:
    id: str
    type: str
    created_at: datetime
    last_digits: str
    holder_name: str
    expiration_month: int
    expiration_year: int
    brand: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CardToken":
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        return cls(**data)

@dataclass
class Charge:
    id: str
    amount: int
    currency: str
    status: str
    payment_method: str
    description: Optional[str]
    customer: Customer
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Charge":
        # Copy data to avoid modifying the original
        data = data.copy()
        
        # Convert customer if it's a dict
        if isinstance(data["customer"], dict):
            data["customer"] = Customer(**data["customer"])
        
        # Convert created_at if it's a string
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        
        return cls(**data)

    def refund(self, amount: Optional[int] = None) -> "Refund":
        from .client import BarteClient
        return BarteClient.get_instance().refund_charge(self.id, {"amount": amount} if amount else None)

    def cancel(self) -> "Charge":
        from .client import BarteClient
        return BarteClient.get_instance().cancel_charge(self.id)

@dataclass
class PixCharge(Charge):
    qr_code: Optional[str] = None
    qr_code_image: Optional[str] = None
    copy_and_paste: Optional[str] = None

    def get_qr_code(self) -> "PixCharge":
        from .client import BarteClient
        qr_data = BarteClient.get_instance().get_pix_qrcode(self.id)
        self.qr_code = qr_data.qr_code
        self.qr_code_image = qr_data.qr_code_image
        self.copy_and_paste = qr_data.copy_and_paste
        return self

@dataclass
class Refund:
    id: str
    charge_id: str
    amount: int
    status: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Refund":
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        return cls(**data)

@dataclass
class InstallmentSimulation:
    installments: int
    amount: int
    total: int
    interest_rate: float

@dataclass
class InstallmentOptions:
    installments: List[InstallmentSimulation]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallmentOptions":
        options = [InstallmentSimulation(**item) for item in data["installments"]]
        return cls(installments=options)

@dataclass
class PixQRCode:
    qr_code: str
    qr_code_image: str
    copy_and_paste: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PixQRCode":
        return cls(**data) 