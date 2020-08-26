from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("fetch/", views.FetchCourses.as_view()),
    path("register/", views.CreateUserView.as_view()),
    path("upload/", views.ProcessAuditView.as_view()),
    path("login/", views.Login.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
