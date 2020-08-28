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
        semester = Semester.objects.create(
            number=validated_data["number"],
            term=validated_data["term"],
            year=validated_data["year"],
            notes=validated_data["notes"],
            user=self.context["request"].user,
        )
        for addedCourse in validated_data["courses"]:
            category = Category.objects.get(name=addedCourse["category"])
            course, created = category.courses.get_or_create(
                code=addedCourse["code"],
                defaults={
                    "name": addedCourse["name"],
                    "code": addedCourse["code"],
                    "credits": addedCourse["credits"],
                    "credits_required": addedCourse["credits"],
                    "inProgress": True,
                    "description": "User Added Course",
                    "category": category,
                },
            )
            course.save()
            if not created:
                print("course existed")
                course.credits = addedCourse["credits"]
                course.inProgress = True
                course.save()
            else:
                print("created new course")
            semester.courses.add(course.id)
        semester.save()

        return semester

    class Meta:
        model = Semester
        fields = ("courses", "number", "term", "year", "notes")


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("label", "number_of_requirements")
