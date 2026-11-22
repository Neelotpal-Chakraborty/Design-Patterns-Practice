'''Why this is better
Single place for instantiation: All constructor arguments and defaults live in the factory
registration, keeping CheckoutService clean and focused on business flow.

Easy extension: New payment methods can be registered without modifying CheckoutService.

Test-friendly: You can pass a mock/stub factory or register a FakeGateway in tests without
touching production code.

Quick Distinction to Keep in Mind
Factory Method uses subclassing (a subclass overrides a create_gateway() method to decide
which concrete product to return).

Simple / Registry Factory (shown above) uses a creator class/map to keep client code
decoupled from concrete constructors—often cleaner in Python than deep class hierarchies.

Abstract Factory creates families of related objects together (for example, a
RazorpayFactory creating a RazorpayOrderClient, RazorpayRefundClient, and
RazorpayWebhookVerifier that must stay compatible with one another).'''


from abc import ABC, abstractmethod
from typing import Callable, Dict, Any


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_inr: float) -> str:
        ...


class UpiGateway(PaymentGateway):
    def __init__(self, vpa_timeout_sec: int = 300):
        self.vpa_timeout_sec = vpa_timeout_sec

    def charge(self, amount_inr: float) -> str:
        return f"UPI intent created for ₹{amount_inr}"


class CardGateway(PaymentGateway):
    def __init__(self, merchant_id: str, three_ds: bool = True):
        self.merchant_id = merchant_id
        self.three_ds = three_ds

    def charge(self, amount_inr: float) -> str:
        return f"Card auth (3DS={self.three_ds}) for ₹{amount_inr}"


class NetBankingGateway(PaymentGateway):
    def __init__(self, bank_code: str):
        self.bank_code = bank_code

    def charge(self, amount_inr: float) -> str:
        return f"NetBanking redirect ({self.bank_code}) for ₹{amount_inr}"


class PaymentGatewayFactory:
    def __init__(self) -> None:
        self._creators: Dict[str, Callable[[Dict[str, Any]], PaymentGateway]] = {}

    def register(self, method: str, creator: Callable[[Dict[str, Any]], PaymentGateway]) -> None:
        self._creators[method.lower()] = creator

    def create(self, method: str, config: Dict[str, Any] | None = None) -> PaymentGateway:
        key = method.lower()
        if key not in self._creators:
            raise ValueError(f"Unsupported payment method: {method}")
        return self._creators[key](config or {})


class CheckoutService:
    def __init__(self, gateway_factory: PaymentGatewayFactory) -> None:
        self._gateway_factory = gateway_factory

    def process_payment(self, method: str, amount_inr: float, config: Dict[str, Any] | None = None) -> str:
        gateway = self._gateway_factory.create(method, config)
        return gateway.charge(amount_inr)


# --- Wiring & Usage ---
factory = PaymentGatewayFactory()
factory.register("upi", lambda cfg: UpiGateway(vpa_timeout_sec=cfg.get("timeout", 300)))
factory.register("card", lambda cfg: CardGateway(
    merchant_id=cfg["merchant_id"],
    three_ds=cfg.get("three_ds", True),
))
factory.register("netbanking", lambda cfg: NetBankingGateway(bank_code=cfg["bank_code"]))

checkout = CheckoutService(factory)
print(checkout.process_payment("upi", 1499.0, {"timeout": 180}))
print(checkout.process_payment("card", 4999.0, {"merchant_id": "M_1029", "three_ds": True}))