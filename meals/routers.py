from rest_framework.routers import DefaultRouter
from .views import MealCategoryViewSet, MealViewSet, QRCodeViewSet, SubCategoryViewSet
from django.urls import path, include
router = DefaultRouter()

router.register(r'mealcategory', MealCategoryViewSet)
router.register(r'meals', MealViewSet)
router.register(r'qr', QRCodeViewSet)
router.register(r'subcategory', SubCategoryViewSet)
