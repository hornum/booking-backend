class PaymentError(Exception):
    pass


class InvalidPaymentAmount(PaymentError):
    pass


class InvalidPaymentStatusTransition(PaymentError):
    pass


class PaymentNotFound(PaymentError):
    pass


class InvalidSignature(PaymentError):
    pass
