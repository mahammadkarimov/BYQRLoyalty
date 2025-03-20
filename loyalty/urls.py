from django.urls import path
from loyalty.views import CreateOrderAPIView

urlpatterns = [
    path('iiko/create/order/', CreateOrderAPIView.as_view(), name='create_order_iiko'),
]


