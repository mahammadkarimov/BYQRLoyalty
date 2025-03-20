from .models import MealCategory, SubCategory, Meal, MealSize
from modeltranslation.translator import TranslationOptions, register

@register(MealCategory)
class MealCategoryTranslationOptions(TranslationOptions):
    fields=('name',)


@register(SubCategory)
class SubCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Meal)
class MealTranslationOptions(TranslationOptions):
    fields = ('name', 'ingredient')


@register(MealSize)
class MealSizeTranslationOptions(TranslationOptions):
    fields = ('size',)