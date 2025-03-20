from rest_framework.routers import DefaultRouter
from .views import DiscountView

router = DefaultRouter()

router.register(r'discounts', DiscountView)

