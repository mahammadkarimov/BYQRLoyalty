from django.contrib import admin
from . models import Table, Reservation, TableCategory, WaiterFeedback, PopularOffer
# Register your models here.

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['name', 'table_id','category', 'current_waiter', 'is_available']
    list_display_links = ['name', 'table_id','category', 'current_waiter', 'is_available']


@admin.register(TableCategory)
class TableCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'restaurant']
    list_display_links = ['title', 'restaurant']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['table', 'waiter', 'start', 'end', 'is_active']
    list_display_links = ['table', 'waiter', 'start', 'end']


@admin.register(WaiterFeedback)
class WaiterFeedbackAdmin(admin.ModelAdmin):
    list_display = ['waiter', 'rate', 'table', 'created_at']
    list_display_links = ['waiter', 'rate', 'table', 'created_at']


admin.site.register(PopularOffer)