from django.urls import path
from .views import (
    QuestionListCreateView,
    QuestionListView,
    QuestionRetriveUpdateDeleteView,
    BulkFeedbackCreateView,
    FeedbackListView,
    FeedbackAnswersListByQuestionView,
    QuestionWithAnswersListView,
    FeedbackStatisticView,
    FeedbackretrieveView
)

urlpatterns = [
    path('feedback/question', QuestionListCreateView.as_view()),
    path('feedback/question/<str:lang>/<str:username>', QuestionListView.as_view()),
    path('feedback/question/<int:question_id>', QuestionRetriveUpdateDeleteView.as_view()),
    path('feedback', BulkFeedbackCreateView.as_view()),
    path('feedback/list', FeedbackListView.as_view()),
    path('feedback/list/<int:question_id>', FeedbackAnswersListByQuestionView.as_view()),
    path('feedback/question-with-feedback', QuestionWithAnswersListView.as_view()),
    path('feedback/statistic', FeedbackStatisticView.as_view()),
    path('feedback/detail/<int:id>', FeedbackretrieveView.as_view()),
]
