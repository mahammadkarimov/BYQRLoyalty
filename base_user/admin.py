from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from modeltranslation.admin import TranslationAdmin
from .models import (
    Waiter,
    Client,
    Interest,
    Restaurant,
    Hotel,
    RestaurantPackage,
    Feature,
    Url,
    RetaurantLanguage,
    Currency,
    Unit,
    RestaurantCampaign,
    RestaurantReview,
    RestaurantStory,
    FavoriteRestaurant,
    RestaurantWorkingHour,
    RestaurantEvent,
    EventImages,
    EventTypes,
    EventGenres,
    Museum,
    RestaurantCategory,
    RestaurantSubCategory,
    LoyalUser, LoyaltyCards
)

User = get_user_model()

admin.site.register(RestaurantEvent)
admin.site.register(EventImages)
admin.site.register(EventTypes)
admin.site.register(EventGenres)
admin.site.register(LoyaltyCards)
admin.site.register(LoyalUser)


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ["email", "first_name", "last_name", 'username', 'user_type']
    list_display_links = ["email", "first_name", "last_name", 'username', 'user_type']
    search_fields = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'profile_photo', 'gender', 'user_type')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}))


@admin.register(Waiter)
class WaiterAdmin(ImportExportModelAdmin):
    list_display = ["get_first_name", "get_last_name", "waiter_id", "balance", "restaurant"]
    list_display_links = ["get_first_name", "get_last_name", "waiter_id", "balance", "restaurant"]
    list_filter = ["restaurant"]

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    list_display = ["get_first_name", "get_last_name"]
    list_display_links = ["get_first_name", "get_last_name"]

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_username(self, obj):
        return obj.user.usename

    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'
    get_email.short_description = 'Email'
    get_username.short_description = 'Username'


@admin.register(Interest)
class InterestAdmin(ImportExportModelAdmin):
    list_display = ['title']


@admin.register(Restaurant)
class RestaurantAdmin(ImportExportModelAdmin, TranslationAdmin):
    list_display = ['get_username']

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Name'

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Hotel)
class HotelAdmin(ImportExportModelAdmin, TranslationAdmin):
    list_display = ['get_username']

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Name'

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class UrlInlineAdmin(admin.TabularInline):
    model = Url


@admin.register(RestaurantPackage)
class RestaurantPackageAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    inlines = [UrlInlineAdmin]


@admin.register(Feature)
class FunctionalityAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['currency', 'language']
    list_display_links = ['currency', 'language']


@admin.register(RestaurantCampaign)
class RestaurantLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'created_at']
    list_display_links = ['name', 'restaurant', 'created_at']


@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'client', 'rating']
    list_display_links = ['restaurant', 'client', 'rating']


@admin.register(RestaurantStory)
class RestauantStoryAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'is_activate']
    list_display_links = ['restaurant', 'is_activate']


@admin.register(FavoriteRestaurant)
class FavoriteRestaurantAdmin(admin.ModelAdmin):
    list_display = ['client', 'restaurant', 'created_at']
    list_display_links = ['client', 'restaurant', 'created_at']


@admin.register(RestaurantWorkingHour)
class RestaurantWorkingHourAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'weekday', 'start', 'end']
    list_display_links = ['restaurant', 'weekday', 'start', 'end']


@admin.register(Museum)
class MuseumAdmin(TranslationAdmin):
    class Media:
        js = (

            'modeltranslation/js/tabbed_translation_fields.js',
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
        )

        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


admin.site.register(RetaurantLanguage)
admin.site.register(Unit)
admin.site.register(RestaurantCategory)
admin.site.register(RestaurantSubCategory)

