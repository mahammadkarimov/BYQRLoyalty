from django.urls import path
from .views import (
    QrListByUsernameView,
    QrRetrieveBySlugView,
    MealSearchView,
    FavoriteMealCreateView,
    FavoriteMealDeleteView,
    FavoriteMealListView,
    AllFavoriteMealListView,
    RestaurantDetailsView, RestaurantMealsView,
    MealFilterListView,

)

urlpatterns = [
    path('restaurant/<str:lang>/<str:username>', QrListByUsernameView.as_view()),
    path('restaurant/meal/retrieve/<str:lang>/<str:slug>', QrRetrieveBySlugView.as_view()),
    path('meal/search/<str:lang>/<str:username>/<str:name>', MealSearchView.as_view()),
    path('meal/filter/', MealFilterListView.as_view()),
    path('meal/favorite/create', FavoriteMealCreateView.as_view()),
    path('meal/favorite/delete/<int:id>', FavoriteMealDeleteView.as_view()),
    path('meal/favorite/all-list/<str:lang>', AllFavoriteMealListView.as_view()),
    path('meal/favorite/list/<str:lang>/<str:username>', FavoriteMealListView.as_view()),


    path('restaurant/<str:username>/details/<str:lang>/', RestaurantDetailsView.as_view(), name='restaurant-details'),
    path('restaurant/<str:username>/meals/<str:lang>/', RestaurantMealsView.as_view(), name='restaurant-meals'),
]