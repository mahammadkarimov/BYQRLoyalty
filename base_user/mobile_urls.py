from django.urls import path
from .views import (
    ClientRegisterView,
    ClientLoginView,
    RestaurantListView,
    RestaurantStoryListAllView,
    RestaurantSearchView,
    ClientUpdateView,
    ClientPasswordUpdateView,
    FavoriteRestaurantCreateView,
    FavoriteRestaurantListView,
    FavoriteRestaurantDeleteView,
    ClientInfoView

)

urlpatterns = [
    path('client/register', ClientRegisterView.as_view(), name='client-register'),
    path('client/login/', ClientLoginView.as_view(), name='client-login'),
    path('client/update/', ClientUpdateView.as_view(), name='client-update'),
    path('client-info/', ClientInfoView.as_view(), name='client-detail'),

    path('client/password/update/', ClientPasswordUpdateView.as_view(), name='client-password-update'),
    path('restaurant/list/<str:lang>/<str:longitude>/<str:latitude>', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurant/story/list/all', RestaurantStoryListAllView.as_view(), name='restaurant-story-list-all'),
    path('restaurant/search/<str:lang>/<str:name>', RestaurantSearchView.as_view(), name='restaurant-search'),
    path('favorite-restaurant/create', FavoriteRestaurantCreateView.as_view()),
    path('favorite-restaurant/list/<str:lang>', FavoriteRestaurantListView.as_view()),
    path('favorite-restaurant/delete/<int:id>', FavoriteRestaurantDeleteView.as_view())
]