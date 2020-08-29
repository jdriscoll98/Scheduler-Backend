from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Category, Course, Semester, Program

# serializer to take in search filters
class FetchCoursesSerializer(serializers.Serializer):
    level = serializers.CharField(max_length=200, required=False, allow_blank=True)
    department = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    class_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course_title = serializers.CharField(max_length=200, required=False, allow_blank=True)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ("id", "username", "password")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "description")


class CourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(max_length=200)

    class Meta:
        model = Course
        fields = ("code", "name", "credits", "category", "credits_required", "passed", "inProgress", "description")


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    def create(self, validated_data):
        courses = validated_data.pop("courses")
        validated_data["user"] = self.context["request"].user
        semester = Semester.objects.create(**validated_data)
        for course in courses:
            exisiting_courses = Course.objects.filter(code=course["code"])
            # all courses with this code that exist in the audit should be updated
            if exisiting_courses:
                courseAddedToSemester = False
                for existing_course in exisiting_courses:
                    existing_course.inProgress = True
                    existing_course.credits = course["credits"]
                    # only add course to semester once
                    if not courseAddedToSemester:
                        existing_course.semester = semester
                        courseAddedToSemester = True
                    existing_course.save()
            else:
                # Course is not specified in audit, therefore we manually add it to specified category
                category = course["category"]
                course["category"] = Category.objects.get(name=category)
                new_course = Course.objects.create(**course)
                new_course.semester = semester
                new_course.inProgress = True
                new_course.save()
        semester.save()
        return semester

    class Meta:
        model = Semester
        fields = ("id", "courses", "number", "term", "year", "notes")


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("label", "number_of_requirements")
