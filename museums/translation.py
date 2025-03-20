from .models import Museum, Exhibit
from modeltranslation.translator import register, TranslationOptions


@register(Museum)
class MuseumTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Exhibit)
class ExhibitTranslationOptions(TranslationOptions):
    fields = ("name","sound", "video", "text", "additional_text")
