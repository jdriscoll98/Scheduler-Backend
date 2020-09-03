from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import (
    FetchCoursesSerializer,
    UserSerializer,
    CategorySerializer,
    SemesterSerializer,
    ProgramSerializer,
    CourseSerializer,
    getPrograms,
)
from .utils import parse_audit, reset_courses
from .models import Category, Program, Semester
import requests
import json
from django.contrib.auth import authenticate, login, logout


class FetchCourses(APIView):
    serializer_class = FetchCoursesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = FetchCoursesSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            class_number = data.get("class_number", "")
            course_number = data.get("course_number", "")
            level = data.get("level", "")
            department = data.get("department", "")
            course_title = data.get("course_title", "")
            term_code = data["term_code"]
            if course_title:
                course_title.replace(" ", "+")
            url = f"https://one.uf.edu/apix/soc/schedule/?category=CWSP&class-num={class_number}&course-code={course_number}&course-title={course_title}&cred-srch=&credits=&day-f=&day-m=&day-r=&day-s=&day-t=&day-w=&days=false&dept={department}&eep=&fitsSchedule=false&ge=&ge-b=&ge-c=&ge-d=&ge-h=&ge-m=&ge-n=&ge-p=&ge-s=&hons=false&instructor=&last-control-number=0&level-max=--&level-min=--&no-open-seats=false&online-a=&online-c=&online-h=&online-p=&period-b=&period-e=&prog-level={level}&term={term_code}&wr-2000=&wr-4000=&wr-6000=&writing="
            response = requests.get(url)
            courses = json.loads(response.content)[0]["COURSES"]
            response_data = {}
            response_data["parsed_courses"] = [
                {
                    "code": course["code"],
                    "name": course["name"],
                    "description": course["description"],
                    "credits": course["sections"][0]["credits"],
                    "courseID": course["courseId"],
                }
                for course in courses
            ]
            return Response(data=response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(CreateAPIView):
    model = User
    serializer_class = UserSerializer


class CategoryList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self):
        programs = Program.objects.filter(user=self.request.user)
        return Category.objects.filter(program__in=programs)


class Semesters(ListCreateAPIView):
    model = Semester
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super(Semesters, self).create(request, *args, **kwargs)
        data = {"semester": response.data, "programs": getPrograms(request.user)}
        return Response(data=data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Semester.objects.filter(user=self.request.user)


class UpdateSemesters(RetrieveUpdateDestroyAPIView):
    model = Semester
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        response = super(UpdateSemesters, self).update(request, *args, **kwargs)
        data = {"semester": response.data, "programs": getPrograms(request.user)}
        return Response(data=data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        reset_courses(instance)
        instance.delete()
        data = {"programs": getPrograms(request.user)}
        return Response(data=data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Semester.objects.filter(user=self.request.user)


class ProcessAuditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = json.loads(request.data)
        parse_audit(data, request.user)
        semesters = Semester.objects.filter(user=request.user)
        serializer = SemesterSerializer(semesters, many=True)
        response_data = {"programs": getPrograms(request.user), "semesters": serializer.data}
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class Authenticate(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class ProgramList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        programs = request.user.programs.all()
        data = {"programs": []}
        for program in programs:
            program_serialized = dict(ProgramSerializer(program).data)
            program_serialized["categories"] = []
            for category in program.categories.all():
                category_serialized = dict(CategorySerializer(category).data)
                category_serialized["courses"] = []
                for course in category.courses.all():
                    course_serialized = CourseSerializer(course)
                    category_serialized["courses"].append(course_serialized.data)
                program_serialized["categories"].append(category_serialized)
            data["programs"].append(program_serialized)

        return Response(data=data, status=status.HTTP_200_OK)
