from django.urls import path
from .views import (
    TableCategoryListView,
    TableListView,
    ReservationCreateView,
    ReservationEndView,
    MyReservedTablesView,
    TableCreateAdminView,
    TableCategoriesGetAdminView,
    TableListAdminView,
    TableUpdateAdminView,
    TableDeleteAdminView,
    TableRetrieveView,
    TableHotelAdminListCreateView,
    TableHotelAdminRetrieveUpdateDestroyView,
    TableRetrieveByNAmeView,
    WaiterFeedbackListView,
    WaiterFeedbackDetailView, PopularOffersView
)


urlpatterns=[
    path('restaurant-table/categories/', TableCategoryListView.as_view(), name='categories'),
    path('restaurant-table/', TableListView.as_view(), name='table_list'),
    path('restaurant-table/<str:username>/<str:table_name>', TableRetrieveByNAmeView.as_view(), name='table_by_name'),
    path('restaurant-table/reservation/start/', ReservationCreateView.as_view(), name='reservation_create'),
    path('restaurant-table/reservation/end/<int:table_id>', ReservationEndView.as_view(), name='reservation_end'),
    path('restaurant-table/my-reserved-tables/', MyReservedTablesView.as_view(), name='my_tables'),
    path('restaurant-table-admin/create-table/', TableCreateAdminView.as_view(), name='create_table'),
    path('restaurant-table-admin/categories/', TableCategoriesGetAdminView.as_view(), name='restaurant_categories'),
    path('restaurant-table-admin/tables/', TableListAdminView.as_view(), name='restaurant_tables'),
    path('restaurant-table-admin/table/update/<int:table_id>', TableUpdateAdminView.as_view(), name='table_update'),
    path('restaurant-table-admin/table/delete/<int:table_id>', TableDeleteAdminView.as_view(), name='table_delete'),
    path('restaurant-table-admin/table/get/<int:table_id>', TableRetrieveView.as_view(), name='table_retrieve'),
    path('hotel-restaurant-table-admin/table-list-create/<str:username>', TableHotelAdminListCreateView.as_view(), name='table_hotel_admin_list_create'),
    path('hotel-restaurant-table-admin/table/<str:slug>', TableHotelAdminRetrieveUpdateDestroyView.as_view(), name='table_hotel_admin_retrieve_update_delete'),
    path('restaurant-admin-feedback/waiter/detail/<int:id>', WaiterFeedbackDetailView.as_view(), name='waiter_feedback_detail'),
    path('restaurant-admin-feedback/waiter/', WaiterFeedbackListView.as_view(), name='waiter_feedback_list'),


    #mobile
    path('mobile/offers/', PopularOffersView.as_view(), name='popular-offers')
]