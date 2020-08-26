from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import FetchCoursesSerializer, UserSerializer
from .utils import parse_audit
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
            if course_title:
                course_title.replace(" ", "+")
            url = f"https://one.uf.edu/apix/soc/schedule/?category=CWSP&class-num={class_number}&course-code={course_number}&course-title={course_title}&cred-srch=&credits=&day-f=&day-m=&day-r=&day-s=&day-t=&day-w=&days=false&dept={department}&eep=&fitsSchedule=false&ge=&ge-b=&ge-c=&ge-d=&ge-h=&ge-m=&ge-n=&ge-p=&ge-s=&hons=false&instructor=&last-control-number=0&level-max=--&level-min=--&no-open-seats=false&online-a=&online-c=&online-h=&online-p=&period-b=&period-e=&prog-level={level}&term=2208&wr-2000=&wr-4000=&wr-6000=&writing="
            response = requests.get(url)
            courses = json.loads(response.content)[0]["COURSES"]
            response_data = {}
            response_data["parsed_courses"] = []
            for course in courses:
                parsed_course = {
                    "code": course["code"],
                    "name": course["name"],
                    "description": course["description"],
                    "credits": course["sections"][0]["credits"],
                }
                response_data["parsed_courses"].append(parsed_course)
            return Response(data=response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(CreateAPIView):
    model = User
    serializer_class = UserSerializer


class ProcessAuditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = json.loads(request.data)
        parsed_audit = parse_audit(data, request.user)
        return Response(status.HTTP_200_OK)


class Authenticate(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})

