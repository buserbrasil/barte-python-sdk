from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from dacite import Config
from dateutil.parser import parse as parse_date

# Default config for dacite with datetime conversion
DACITE_CONFIG = Config(
    type_hooks={datetime: lambda x: parse_date(x) if isinstance(x, str) else x}
)


@dataclass
class Customer:
    name: str
    tax_id: str
    email: str


@dataclass
class CardToken:
    uuid: str
    status: str
    createdAt: datetime
    brand: str
    cardHolderName: str
    cvvChecked: bool
    fingerprint: str
    first6digits: str
    last4digits: str
    buyerId: str
    expirationMonth: str
    expirationYear: str
    cardId: str


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
    installments: Optional[int] = None
    installment_amount: Optional[int] = None

    def refund(self, amount: Optional[int] = None) -> "Refund":
        from .client import BarteClient

        return BarteClient.get_instance().refund_charge(
            self.id, {"amount": amount} if amount else None
        )

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


@dataclass
class InstallmentSimulation:
    installments: int
    amount: int
    total: int
    interest_rate: float


@dataclass
class InstallmentOptions:
    installments: List[InstallmentSimulation]


@dataclass
class PixQRCode:
    qr_code: str
    qr_code_image: str
    copy_and_paste: str


@dataclass
class Buyer:
    uuid: str
    document: str
    name: str
    countryCode: str
    phone: str
    email: str
    alternativeEmail: str


@dataclass
class SortInfo:
    unsorted: bool
    sorted: bool
    empty: bool


@dataclass
class Pageable:
    sort: SortInfo
    pageNumber: int
    pageSize: int
    offset: int
    paged: bool
    unpaged: bool


@dataclass
class BuyerList:
    content: List[Buyer]
    pageable: Pageable
    totalPages: int
    totalElements: int
    last: bool
    numberOfElements: int
    size: int
    number: int
    sort: SortInfo
    first: bool
    empty: bool
