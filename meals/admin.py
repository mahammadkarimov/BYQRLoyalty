from django.contrib import admin
from .models import MealCategory, Meal, SubCategory, MealImage, MealSize, Basket, BasketItem, Order, FavoriteMeal, Cousine, MealReview
from import_export.admin import ImportExportModelAdmin
from modeltranslation.admin import TranslationAdmin


# Register your models here.
@admin.register(MealImage)
class MealImageAdmin(admin.ModelAdmin):
    list_display = ['meal']


@admin.register(MealSize)
class MealSizeAdmin(TranslationAdmin):
    list_display = ['id', 'size', 'meal', 'price']
    list_display_links = ['id', 'size', 'meal', 'price']

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class MealSizeInlineAdmin(admin.TabularInline):
    model = MealSize


class MealImageInlineAdmin(admin.TabularInline):
    model = MealImage


@admin.register(MealCategory)
class MealCategoryAdmin(ImportExportModelAdmin, TranslationAdmin):
    group_fieldsets = True  
    list_display = ["name", "get_restaurant"]
    list_display_links = ["name", "get_restaurant"]
    search_fields = ["name"]

        
    def get_restaurant(self, obj):
        try:
            return obj.created_from.user.username
        except:
            return '-'
    
    
    get_restaurant.short_description = 'Restaurant'

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Meal)
class Meal(ImportExportModelAdmin, TranslationAdmin):
    list_display = ['name', 'category', 'get_restaurant']
    list_display_links = ['name', 'category', 'get_restaurant']
    inlines = [MealImageInlineAdmin, MealSizeInlineAdmin]
    search_fields = ['name', 'category__name']
    def get_restaurant(self, obj):
        return obj.created_from.user.username
    
    
    get_restaurant.short_description = 'Restaurant'
    group_fieldsets = True 
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(SubCategory)
class SubCategory(ImportExportModelAdmin, TranslationAdmin):
    list_display = ['name', 'main_category', 'created_from']
    list_display_links = ['name', 'main_category', 'created_from']
    search_fields = ['name']
    group_fieldsets = True 
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }



@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['client', 'created_at', 'is_completed']
    list_display_links = ['client', 'created_at', 'is_completed']
    search_fields = ['client__user__username']


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ['meal', 'basket', 'quantity']
    list_display_links = ['meal', 'basket', 'quantity']
    search_fields = ['meal__name', 'basket__client__user__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['client', 'basket', 'is_completed']
    list_display_links = ['client', 'basket', 'is_completed']
    search_fields = ['client__user__username']


@admin.register(FavoriteMeal)
class FavoriteMealAdmin(admin.ModelAdmin):
    list_display = ['client', 'meal', 'created_at']
    list_display_links = ['client', 'meal', 'created_at']
    search_fields = ['client__user__username', 'meal__name']


@admin.register(MealReview)
class MealReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal', 'rating', 'created_at', 'updated_at']
    list_display_links = ['user', 'meal', 'rating', 'created_at', 'updated_at']

admin.site.register(Cousine)