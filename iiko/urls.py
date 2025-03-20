from django.urls import path
from . import views

urlpatterns = [
    path('iiko/create_order/<str:organization_id>/<str:terminal_group_id>/<str:table_id>/<str:product_id>/', views.create_order_view, name='create_order'),
    path('iiko/fetch_menu/<str:organization_id>/', views.fetch_menu_view, name='fetch_menu'),
    path('iiko/available-tables/<str:terminal_group_id>/', views.get_available_tables, name='available_tables'),
    path('iiko/orders_by_table/<str:organization_id>/<str:table_id>/', views.get_orders_by_table,
         name='get_orders_by_table'),

]
