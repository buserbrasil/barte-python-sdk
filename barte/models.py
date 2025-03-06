from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Literal
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
class ChargerCustomer:
    uuid: str
    document: str
    type: str
    name: str
    email: str
    phone: str
    alternativeEmail: Optional[str]


@dataclass
class Charge:
    uuid: str
    title: str
    expirationDate: datetime
    value: float
    paymentMethod: str
    status: str
    customer: ChargerCustomer
    paidDate: Optional[datetime]
    authorizationCode: Optional[str]
    authorizationNsu: Optional[str]

    def refund(self, as_fraud: Optional[bool] = False) -> "Refund":
        from .client import BarteClient

        return BarteClient.get_instance().refund_charge(self.uuid, as_fraud)

    def cancel(self) -> "Charge":
        from .client import BarteClient

        return BarteClient.get_instance().cancel_charge(self.uuid)


@dataclass
class OrderCustomer:
    document: str
    type: str
    documentCountry: str | None
    name: str
    email: str
    phone: str
    alternativeEmail: Optional[str]


@dataclass
class OrderCharge:
    uuid: str
    title: str
    expirationDate: datetime
    value: float
    paymentMethod: str
    status: str
    customer: OrderCustomer
    authorizationCode: Optional[str] = None
    authorizationNsu: Optional[str] = None
    paidDate: Optional[datetime] = None


@dataclass
class Order:
    uuid: str
    status: str
    title: str
    description: str
    value: float
    installments: int
    startDate: datetime
    payment: str
    customer: OrderCustomer
    idempotencyKey: str
    charges: List[OrderCharge]

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
    pixCode: str
    pixQRCodeImage: str
    paidDate: Optional[datetime]

    def get_qr_code(self) -> "PixCharge":
        from .client import BarteClient

        qr_data = BarteClient.get_instance().get_pix_qrcode(self.uuid)
        self.qr_code = qr_data.pixCode
        self.qr_code_image = qr_data.pixQRCodeImage
        return self


@dataclass
class Refund(Charge):
    pass


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
    alternativeEmail: Optional[str]


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
class BaseListReponse:
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


@dataclass
class BuyerList(BaseListReponse):
    content: List[Buyer]


@dataclass
class ChargeList(BaseListReponse):
    content: List[Charge]


@dataclass
class Card:
    holderName: str
    number: str
    expiration: str
    cvv: str


@dataclass
class InternationalDocument:
    documentNumber: str
    documentType: str
    documentNation: str


@dataclass
class BillingAddress:
    country: str
    state: str
    city: str
    district: str
    street: str
    zipCode: str
    number: Optional[str]
    complement: Optional[str]


@dataclass
class FraudData:
    name: str
    email: str
    phone: str
    billingAddress: BillingAddress
    internationalDocument: Optional[InternationalDocument]
    document: Optional[str]


@dataclass
class Payment:
    method: Literal[
        "PIX",
        "BANK_SLIP",
        "CREDIT_CARD",
        "CREDIT_CARD_EARLY_BUYER",
        "CREDIT_CARD_EARLY_SELLER",
        "DEBIT_CARD",
        "CREDIT_CARD_EARLY_MIXED",
        "GOOGLE_PAY",
        "APPLE_PAY",
        "INVALID",
    ]
    brand: Optional[str]
    cardToken: Optional[str]
    capture: Optional[bool]
    integrationOrderId: Optional[str]
    card: Optional[Card]
    fraudData: Optional[FraudData]


@dataclass
class SubSellerPayment:
    idSubSeller: int
    amount: int
    paymentValue: int
    paymentType: str


@dataclass
class SubSellerPaymentRequest:
    subSellerPayment: List[SubSellerPayment]


@dataclass
class Metadata:
    key: str
    value: str


@dataclass
class OrderPayload:
    title: str
    uuidBuyer: str
    startDate: str
    value: int
    installments: int
    payment: Payment
    attemptReference: Optional[str]
    urlCallBack: Optional[str]
    description: Optional[str]
    subSellerPaymentRequest: Optional[SubSellerPaymentRequest]
    metadata: Optional[List[Metadata]]


@dataclass
class InstallmentOption:
    installments: int
    installmentAmount: float
    totalAmount: float


@dataclass
class BuyerCard:
    uuid: str
    status: str
    createdAt: datetime
    brand: str
    first6digits: str
    last4digits: str
    buyerId: str
    expirationMonth: str
    expirationYear: str
    cardId: str
