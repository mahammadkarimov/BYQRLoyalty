from django.contrib import admin
from .models import Question, Feedback, FeedbackDescription
from modeltranslation.admin import TranslationAdmin
# Register your models here.

@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    list_display = ['user', 'question']
    list_display_links = ['user', 'question']
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
    list_display = ['overall_rating', 'instance', 'created_at']
    list_display_links = ['overall_rating', 'instance', 'created_at']