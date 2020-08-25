from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FetchCoursesSerializer
import requests
import json


class FetchCourses(APIView):
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
            print(url)
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
