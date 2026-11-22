'''Imagine you are building the checkout backend for an Indian e-commerce platform.
Customers pay via UPI, Credit/Debit Card, or NetBanking, and each gateway has its own
SDK/client, authentication headers, and payload formatting.

Where the Factory Pattern fits: Your checkout service shouldn't know how to construct a
UPI client versus a Card client or NetBanking client—it just needs a ready-to-use
PaymentGateway object based on the selected payment_method. Adding a new rail 
(say,RuPay/BNPL or a backup Razorpay/Stripe adapter) should mean adding a new class 
and registering it, not hunting down if/else chains across billing, refunds, and webhooks.

Where it doesn't fit: If you only have one fixed payment provider and no expectation of
multiple implementations or runtime selection, a factory adds indirection without payoff.'''


class UpiGateway:
    def __init__(self, vpa_timeout_sec: int):
        self.vpa_timeout_sec = vpa_timeout_sec

    def charge(self, amount_inr: float) -> str:
        return f"UPI intent created for ₹{amount_inr}"


class CardGateway:
    def __init__(self, merchant_id: str, three_ds: bool):
        self.merchant_id = merchant_id
        self.three_ds = three_ds

    def charge(self, amount_inr: float) -> str:
        return f"Card auth (3DS={self.three_ds}) for ₹{amount_inr}"


class NetBankingGateway:
    def __init__(self, bank_code: str):
        self.bank_code = bank_code

    def charge(self, amount_inr: float) -> str:
        return f"NetBanking redirect ({self.bank_code}) for ₹{amount_inr}"


class CheckoutService:
    def process_payment(self, method: str, amount_inr: float, **options) -> str:
        # Tightly coupled: caller knows exact constructors & config details of every gateway
        if method == "upi":
            gateway = UpiGateway(vpa_timeout_sec=options.get("timeout", 300))
        elif method == "card":
            gateway = CardGateway(
                merchant_id=options["merchant_id"],
                three_ds=options.get("three_ds", True),
            )
        elif method == "netbanking":
            gateway = NetBankingGateway(bank_code=options["bank_code"])
        else:
            raise ValueError(f"Unsupported payment method: {method}")

        return gateway.charge(amount_inr)