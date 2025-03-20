from django.contrib import admin
from .models import TechnicalService, Service, Question, Feedback, FeedbackDescription, HotelRoom,ServiceImages
from modeltranslation.admin import TranslationAdmin
# Register your models here.


@admin.register(TechnicalService)
class TechnicalServiceAdmin(TranslationAdmin):
    list_display = ['title', 'hotel']
    list_display_links = ['title', 'hotel']
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

class ServiceImagesAdmin(admin.StackedInline):
    model = ServiceImages
    extra = 1

@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    list_display = ['title', 'price', 'hotel']
    list_display_links = ['title', 'price', 'hotel']
    group_fieldsets = True
    inlines = [ServiceImagesAdmin]

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    list_display = ['hotel', 'question']
    list_display_links = ['hotel', 'question']
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

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['description', 'rating']
    list_display_links = ['description', 'rating']


@admin.register(FeedbackDescription)
class FeedbackDescriptionAdmin(admin.ModelAdmin):
    list_display = ['overall_rating', 'room', 'created_at']
    list_display_links = ['overall_rating', 'room', 'created_at']


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_id', 'hotel']
    list_display_links = ['name', 'room_id', 'hotel']
