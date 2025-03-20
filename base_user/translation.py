from modeltranslation.translator import TranslationOptions, register
from .models import Restaurant, Hotel

@register(Restaurant)
class RestaurantTranslationOptions(TranslationOptions):
    fields = ('address',)


@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('address', )