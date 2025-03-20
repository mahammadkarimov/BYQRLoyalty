from django.contrib import admin
from .models import Exhibit
from modeltranslation.admin import TranslationAdmin





@admin.register(Exhibit)
class ExhibitAdmin(TranslationAdmin):
    class Media:
        js = (

            'modeltranslation/js/tabbed_translation_fields.js',
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
        )

        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }




