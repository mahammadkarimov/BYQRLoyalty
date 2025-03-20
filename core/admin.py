from django.contrib import admin
from .models import (
    RestaurantDiscounts,
    Payment,
    Currency,
    UserFAQ
)
admin.site.register(RestaurantDiscounts)
# Register your models here.

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'net', 'currency', 'waiter', 'order_id', 'transaction_id', 'created_at', 'card_name', 'card_mask', 'is_successful', 'is_completed']
    list_display_links = ['amount', 'net', 'currency', 'waiter', 'order_id', 'transaction_id', 'created_at', 'card_name', 'card_mask', 'is_successful', 'is_completed']


@admin.register(UserFAQ)
class UserFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_at']
    list_display_links = ['question', 'created_at']