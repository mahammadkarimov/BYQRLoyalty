from django.urls import path
from .views import (
    CurrencyListView,
    PaymentCreateView,
    PaymentCallBackView,
    PaymentStatusView,
    CardRegisterView,
    PayWithSavedCardView,
    PayAndSaveCardView,
    CreateRefundView,
    WaiterPaymentListView,
    TokenPaymentCreateView,
    ApplePaySessionView,
    ApplePayView, ContactFormView,
    GenerateEPointTokenView,
)


urlpatterns = [
    path('payment/currencies', CurrencyListView.as_view(), name='curreny_list'),
    path('payment/create', PaymentCreateView.as_view(), name='payment_create'),
    path('payment/token/create', TokenPaymentCreateView.as_view(), name='payment_token_create'),
    path('payment/callback', PaymentCallBackView.as_view(), name='payment_call_back'),
    path('payment/status', PaymentStatusView.as_view(), name='payment_status'),
    path('payment/apple-pay-session', ApplePaySessionView.as_view(), name='apple-pay-session'),
    path('payment/card-register', CardRegisterView.as_view(), name='card_register'),
    path('payment/pay-with-saved-card', PayWithSavedCardView.as_view(), name='pay_with_saved_card'),
    path('payment/pay-and-save-card', PayAndSaveCardView.as_view(), name='pay_and_save_card'),
    path('payment/create-refund', CreateRefundView.as_view(), name='create_refund'),
    path('payment/apple-pay', ApplePayView.as_view()),
    path('waiter/tips/', WaiterPaymentListView.as_view()),
    path('corporative-contact/', ContactFormView.as_view(), name='contact-form'),
    path("wallet-pay/", GenerateEPointTokenView.as_view(), name='generate-epoint-wallet'),

]
