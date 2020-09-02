from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Category, Course, Semester, Program
from .utils import set_courses, reset_courses

# serializer to take in search filters
class FetchCoursesSerializer(serializers.Serializer):
    level = serializers.CharField(max_length=200, required=False, allow_blank=True)
    department = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    class_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    term_code = serializers.CharField(max_length=200)


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
    id = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = Course
        fields = ("id", "code", "name", "credits", "category", "credits_required", "passed", "inProgress", "description")


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    def validate(self, data):
        if not data.get("courses"):
            raise serializers.ValidationError("Semester must contain at least one course")

        # Check that a course could be processed as auto
        for course in data["courses"]:
            if course["code"] == "User-Added" and course["category"] == "Auto":
                raise serializers.ValidationError("All placeholder courses must specifiy a category")

            exisiting_course = Course.objects.filter(user=self.context["request"].user, code=course["code"], semester=None)
            if course["category"] == "Auto":
                if not exisiting_course.exists():
                    raise serializers.ValidationError(
                        f"Could not auto generate a category for course {course['code']}, please double check its audit requirement"
                    )

        # Semester term + year is unique, but by pass if updating
        existing_semester = Semester.objects.filter(user=self.context["request"].user, term=data["term"], year=data["year"])
        if existing_semester.exists():
            if self.instance:
                if self.instance.pk != existing_semester.first().pk:
                    raise serializers.ValidationError("ERROR: A Semester with this term and year already exists")
            else:
                raise serializers.ValidationError("ERROR: A Semester with this term and year already exists")

        return super(SemesterSerializer, self).validate(data)

    def update(self, instance, validated_data):
        # Update Term / Year / Notes
        instance.term = validated_data["term"]
        instance.year = validated_data["year"]
        instance.notes = validated_data["notes"]

        # Update Courses
        reset_courses(instance)
        instance.courses.clear()
        set_courses(validated_data["courses"], instance, self.context["request"].user)

        instance.save()
        return instance

    def create(self, validated_data):
        courses = validated_data.pop("courses")
        # Create Semester
        validated_data["user"] = self.context["request"].user
        semester = Semester.objects.create(**validated_data)
        semester.save()
        # Add Courses
        set_courses(courses, semester, self.context["request"].user)
        return semester

    class Meta:
        model = Semester
        fields = ("id", "courses", "number", "term", "year", "notes")


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("label", "number_of_requirements")


def getPrograms(user):
    programs = user.programs.all()
    serialized_programs = []
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
        serialized_programs.append(program_serialized)
    return serialized_programs
