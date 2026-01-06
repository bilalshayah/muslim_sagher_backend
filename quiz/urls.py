from django.urls import path
from .views import (
    # User APIs
    VideoQuestionsView,
    SubmitQuizView,

    # Admin APIs
    QuestionCreateView,
    QuestionDetailView,
    AnswerChoiceCreateView,
    AnswerChoiceDetailView,
    AdminVideoQuestionsView
)

urlpatterns = [

    # -----------------------------------------------------
    # User-facing APIs (الطفل)
    # -----------------------------------------------------
    path("video/<int:video_id>/questions/", VideoQuestionsView.as_view(), name="video-questions"),
    path("video/<int:video_id>/submit/", SubmitQuizView.as_view(), name="submit-quiz"),


    # -----------------------------------------------------
    # Dashboard APIs (الآدمن)
    # -----------------------------------------------------

    # Questions CRUD
    path("dashboard/questions/create/", QuestionCreateView.as_view(), name="question-create"),
    path("dashboard/questions/<int:pk>/", QuestionDetailView.as_view(), name="question-detail"),

    # Answer Choices CRUD
    path("dashboard/choices/create/", AnswerChoiceCreateView.as_view(), name="choice-create"),
    path("dashboard/choices/<int:pk>/", AnswerChoiceDetailView.as_view(), name="choice-detail"),

    # Answer And Choices And Correct Choice CURD
    path("admin/videos/<int:video_id>/questions/", AdminVideoQuestionsView.as_view()),
]