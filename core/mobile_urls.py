from django.urls import path
from .views import UserFAQLisView

urlpatterns = [
    path('client/faq/list', UserFAQLisView.as_view()),
]