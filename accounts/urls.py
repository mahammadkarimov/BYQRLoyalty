from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import RestaurantRegisterView,MyObtainTokenPairView
urlpatterns=[
     # path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
     path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
     path("register/",RestaurantRegisterView.as_view(),name="restaurant_register"),
]