from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserGetApi,
    UpdateUserApi,
    WaiterRegisterView,
    waiter_login_view,
    WaiterRetrieveView,
    WaiterListView,
    ClientRegisterView,
    ClientListView,
    ClientRetrieveView,
    hotel_login_view,
    HotelRegisterView,
    HotelListView,
    HotelRetrieveView,
    WaiterProfileView,
    HotelUpdateView,
    HotelAdminGetView,
    HotelWaiterRegisterAdminView,
    HotelWaiterListAdminView,
    WaiterDeleteView,
    WaiterUpdateView,
    WaiterPasswordUpdateView,
    WaiterNotificationTokenUpdateView,
    WaiterGetView,
    WaiterNotifyView,
    WaiterProfileUpdateView,
    RestaurantPacpageView,
    UserTypeView,
    RestaurantCampaignCreateView,
    RestaurantCampaignRetrieveView,
    RestaurantCampaignListView,
    RestaurantCampaignUpdateView,
    RestaurantCampaignDeleteView,
    RestaurantStoryDeleteView,
    RestaurantStoryUpdateView,
    RestautantStoryAdminListView,
    RestaurantStoryCreateView,
    RestaurantStoryListView,
    RestaurantFbpixelGetView,
    RestaurantFbpixelUpdateView,
    RestaurantEventViewSet,
    EventTypesList,
    EventGenresList,
    RestaurantCategoryList,
    RestaurantSubCategoryList,
    MuseumRegisterView,
    ClientLoyalRegisterView, UpdateFCMTokenView,
    LoyalUserRegisterView, LoyalUserLoginView, OTPVerificationView, CreateLoyalCardView

)

from loyalty_latest.api.views import (
    DownloadPassView
)

router = DefaultRouter()
router.register(r'events', RestaurantEventViewSet)

urlpatterns = [
    path("user", UserGetApi.as_view(), name="user"),
    path("userupdate", UpdateUserApi.as_view(), name="user_update"),
    path("waiter/register/", WaiterRegisterView.as_view(), name="waiter_register"),
    path("waiter/login/", waiter_login_view, name="waiter_login"),
    path("waiter/notify/", WaiterNotifyView.as_view(), name="waiter_notify"),
    path("waiter/list/", WaiterListView.as_view(), name="waiter_list"),
    path('waiter/update', WaiterProfileUpdateView.as_view(), name='waiter_update'),
    path("waiter/<str:username>", WaiterRetrieveView.as_view(), name="waiter_retrieve"),
    path("waiter/details/", WaiterProfileView.as_view(), name='waiter_profile'),
    path("waiter/notification-token/update/", WaiterNotificationTokenUpdateView.as_view(),
         name='waiter_notification_token'),
    path("client/register", ClientRegisterView.as_view(), name="client_register"),
    path("client/register/loyal/", ClientLoyalRegisterView.as_view(), name='client-register-loyal'),
    path("client/list/", ClientListView.as_view(), name="client_list"),
    path("client/<str:slug>", ClientRetrieveView.as_view(), name="client_retrieve"),
    path("login/", hotel_login_view, name="hotel_login"),

    path("museum/register/", MuseumRegisterView.as_view(), name='museum-register'),

    path("hotel/register/", HotelRegisterView.as_view(), name="hotel_register"),
    path("hotel/list/", HotelListView.as_view(), name="hotel_list"),
    path("hotel/<str:username>", HotelRetrieveView.as_view(), name="hotel_retrieve"),
    path("hotel/update/", HotelUpdateView.as_view(), name="hotel_update"),
    path("hotel/admin/", HotelAdminGetView.as_view(), name="hotel_admin"),

    path("hotel-restaurant-admin/waiter/register/<str:restaurant_username>", HotelWaiterRegisterAdminView.as_view(),
         name='hotel_waiter_register'),
    path("hotel-restaurant-admin/waiter/list/<str:restaurant_username>", HotelWaiterListAdminView.as_view(),
         name='hotel_waiter_list'),
    path('hotel-restaurant-admin/waiter/update/<str:waiter_slug>', WaiterUpdateView.as_view(), name='waiter_update'),
    path('hotel-restaurant-admin/waiter/password/update/<str:waiter_slug>', WaiterPasswordUpdateView.as_view(),
         name='waiter_password_update'),
    path('hotel-restaurant-admin/waiter/delete/<str:waiter_slug>', WaiterDeleteView.as_view(), name='waiter_delete'),
    path('hotel-restaurant-admin/waiter/get/<str:waiter_slug>', WaiterGetView.as_view(), name='waiter_get'),
    path('hotel-restaurant-admin/user-auth', UserTypeView.as_view()),

    path('restaurant-admin/package', RestaurantPacpageView.as_view()),
    path('restaurant-admin/update/fbpixel', RestaurantFbpixelUpdateView.as_view()),
    path('restaurant-admin/get/fbpixel', RestaurantFbpixelGetView.as_view()),

    path('restaurant-admin-campaign/create', RestaurantCampaignCreateView.as_view(), name='restaurant_campaign_create'),
    path('restaurant-admin-campaign/retrieve/<str:campaign_id>', RestaurantCampaignRetrieveView.as_view(),
         name='restaurant_campaign_retrieve'),
    path('restaurant-admin-campaign/list', RestaurantCampaignListView.as_view(), name='restaurant_campaign_list'),
    path('restaurant-admin-campaign/delete', RestaurantCampaignDeleteView.as_view(), name='restaurant_campaign_delete'),
    path('restaurant-admin-campaign/update/<str:campaign_id>', RestaurantCampaignUpdateView.as_view(),
         name='restaurant_campaign_update'),
    # mobile
    path('mobile/restaurant-categories/', RestaurantCategoryList.as_view(), name='restaurant-categories'),
    path('mobile/restaurant-sub-categories/', RestaurantSubCategoryList.as_view(), name='restaurant-sub-categories'),

    path('restaurant-story/delete/<int:story_id>', RestaurantStoryDeleteView.as_view(), name='restaurant-story-delete'),
    path('restaurant-story/update/<int:story_id>', RestaurantStoryUpdateView.as_view(), name='restaurant-story-update'),
    path('restaurant-story/admin/list', RestautantStoryAdminListView.as_view(), name='restaurant-story-admin-list'),
    path('restaurant-story/create', RestaurantStoryCreateView.as_view(), name='restaurant-story-create'),
    path('restaurant-story/list/<str:restaurant_slug>', RestaurantStoryListView.as_view(),
         name='restaurant-story-list'),
    # path('waiter/login/', login, name='waiter-login'),

    path('', include(router.urls)),
    path("event/genres/", EventGenresList.as_view(), name='event-genres'),
    path("event/types/", EventTypesList.as_view(), name='event-types'),

    path('update-fcm-token/', UpdateFCMTokenView.as_view(), name='update-fcm-token'),
    path('loyal-user/register/', LoyalUserRegisterView.as_view(), name='register-loyal-user'),
    path('loyal/login/', LoyalUserLoginView.as_view(), name='login-loyal-user'),
    path('loyal-user/verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('create-loyal-card/', CreateLoyalCardView.as_view(), name='create-loyal-card'),
    path('download/<str:download_hash>/',DownloadPassView.as_view(),name='DownloadPasses')
]
