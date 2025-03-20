from .models import Question
from modeltranslation.translator import register, TranslationOptions

@register(Question)
class QuetionTranslationOptions(TranslationOptions):
    fields = ('question',)