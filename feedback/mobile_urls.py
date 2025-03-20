from django.urls import path
from .views import (
    BulkFeedbackCreateView,
    QuestionListView
)

urlpatterns = [
    path('feedback/restaurant', BulkFeedbackCreateView.as_view()),
    path('feedback/question/<str:lang>/<str:username>', QuestionListView.as_view()),
]