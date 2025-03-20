from django.contrib import admin
from .models import Layout, UserCard, Passes
from base_user.models import Restaurant, Hotel



@admin.register(Layout)
class LayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'layout_name', 'layout_type', 'user', 'layout_background_color')
    list_filter = ('layout_type', 'user')
    search_fields = ('layout_name', 'user__email')
    autocomplete_fields = ('user',)
    readonly_fields = ('id',)

    fieldsets = (
        (None, {
            'fields': ('layout_name', 'layout_type', 'user')
        }),
        ('Media', {
            'fields': ('layout_banner', 'layout_logo')
        }),
        ('Colors', {
            'fields': ('layout_background_color', 'text_color')
        }),
    )


@admin.register(UserCard)
class UserCardAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'surname', 'email', 'phone_number', 'loyalty_level',
        'bonuses', 'discount', 'is_confirmed', 'layout', 'restaurant', 'hotel'
    )
    list_filter = ('loyalty_level', 'is_confirmed', 'layout', 'restaurant', 'hotel')
    search_fields = ('name', 'surname', 'email', 'phone_number', 'card_number')
    autocomplete_fields = ('layout',  'user')
    readonly_fields = ('id', 'download_hash')

    fieldsets = (
        ('User Info', {
            'fields': ('name', 'surname', 'email', 'phone_number')
        }),
        ('Card Info', {
            'fields': (
                'card_user_id', 'card_number', 'device', 'deviceToken',
                'layout', 'loyalty_level', 'bonuses', 'discount', 'loyalty_balance',
                'download_hash', 'is_confirmed'
            )
        }),
        ('Associations', {
            'fields': ('restaurant', 'hotel', 'user')
        }),
    )


@admin.register(Passes)
class PassesAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_type', 'user_card')
    list_filter = ('device_type',)
    autocomplete_fields = ('user_card',)
    search_fields = ('user_card__name', 'user_card__surname', 'user_card__email')
    readonly_fields = ('id',)
