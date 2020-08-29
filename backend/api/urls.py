from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("fetch/", views.FetchCourses.as_view()),
    path("register/", views.CreateUserView.as_view()),
    path("upload/", views.ProcessAuditView.as_view()),
    path("login/", views.Authenticate.as_view()),
    path("categories/", views.CategoryList.as_view()),
    path("semesters/", views.Semesters.as_view()),
    path("semesters/<int:pk>", views.UpdateSemesters.as_view()),
    path("programs/", views.ProgramList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
