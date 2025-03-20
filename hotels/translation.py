from .models import TechnicalService, Service, Question
from modeltranslation.translator import TranslationOptions, register


@register(TechnicalService)
class TechnicalServiceTranslationAdmin(TranslationOptions):
    fields = ('title',)


@register(Service)
class ServiceTranslationAdmin(TranslationOptions):
    fields = ('title', 'description')


@register(Question)
class QuestionTranslationAdmin(TranslationOptions):
    fields = ('question',)