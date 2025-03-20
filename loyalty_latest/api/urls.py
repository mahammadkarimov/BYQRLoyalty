from django.urls import path
from .views import (
    CreateLayoutAPIView,
    CreateLoyaltyCard,
    LoyaltyLayoutGetView,
    LoyaltyLayoutUpdateView,
    LoyaltyLayoutDeleteView,
    LoyaltyCardsGetView,
    UpdateLoyaltyCard,
    DeleteLoyaltyCard
    )

urlpatterns = [
    path('layouts/create/',CreateLayoutAPIView.as_view(),name='CreateLayout'),
    path('layouts/',LoyaltyLayoutGetView.as_view(),name="LoyaltyLayoutGetView"),
    path('layouts/<int:pk>/update/',LoyaltyLayoutUpdateView.as_view(),name="LoyaltyLayoutUpdateView"),
    path('layouts/<int:pk>/delete/', LoyaltyLayoutDeleteView.as_view(), name='loyalty_layout_delete'),
    path('cards/',LoyaltyCardsGetView.as_view(),name="LoyaltyCardsGetView"),
    path('cards/create/',CreateLoyaltyCard.as_view(),name='CreateLoyaltyCard'),
    path('cards/<str:card_id>/update/',UpdateLoyaltyCard.as_view(),name='UpdateLoyaltyCard'),
    path('cards/<int:card_id>/delete/', DeleteLoyaltyCard.as_view(), name='delete_loyalty_card'),
   ]