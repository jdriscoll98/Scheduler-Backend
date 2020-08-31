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
        fields = ("id", "code", "name", "credits", "category", "credits_required", "passed", "inProgress", "description")


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    def validate(self, data):
        if not data.get("courses"):
            raise serializers.ValidationError("Semester must contain at least one course")
        for course in data["courses"]:
            exisiting_course = Course.objects.filter(user=self.context["request"].user, code=course["code"], name=course["name"], semester=None)
            if course["category"] == "Auto" and not exisiting_course.exists():
                raise serializers.ValidationError(
                    "Could not auto generate a category for one or more courses, please double check each courses audit requirement"
                )
        existing_semester = Semester.objects.filter(user=self.context["request"].user, term=data["term"], year=data["year"])
        if existing_semester.exists():
            if self.instance:
                if self.instance.pk != existing_semester.first().pk:
                    raise serializers.ValidationError("ERROR: A Semester with this term and year already exists")
            else:
                raise serializers.ValidationError("ERROR: A Semester with this term and year already exists")

        return super(SemesterSerializer, self).validate(data)

    def update(self, instance, validated_data):
        # Update Term / Year
        instance.term = validated_data["term"]
        instance.year = validated_data["year"]

        new_courses = validated_data["courses"]
        # Loop through current courses
        for course in instance.courses.all():
            courseFound = False
            for new_course in new_courses:
                # Update course with new category information
                if new_course.get("id"):
                    exisiting_course = Course.objects.get(pk=new_course["id"])
                    exisiting_course.category = new_course["category"]
                    exisiting_course.save()
                    new_courses.remove(new_course)
                    courseFound = True
                    break
            # if code reaches here, course has been deleted
            if not courseFound:
                if course.description == "User Added Course":  # non-audit specifc course
                    course.delete()
                else:  # audit specific course
                    course.inProgress = False
                    course.credits = 0

        for course in new_courses:  # remaining courses to add
            if course["code"] == "User-Added":
                category = course["category"]
                course["category"] = Category.objects.get(name=category, user=self.context["request"].user)
                course["user"] = self.context["request"].user
                new_course = Course.objects.create(**course)
                new_course.semester = instance
                new_course.inProgress = True
                new_course.save()
            else:
                exisiting_courses = Course.objects.filter(code=course["code"], name=course["name"], user=self.context["request"].user)
                if exisiting_courses:
                    # all courses with this code that exist in the audit should be updated
                    for existing_course in exisiting_courses:
                        existing_course.inProgress = True
                        existing_course.credits = course["credits"]
                        existing_course.semester = instance
                        existing_course.save()
                else:
                    # Course is not specified in audit, therefore we manually add it to specified category
                    if category != "Auto":
                        category = course["category"]
                        course["category"] = Category.objects.get(name=category, user=self.context["request"].user)
                        course["user"] = self.context["request"].user
                        new_course = Course.objects.create(**course)
                        new_course.semester = instance
                        new_course.inProgress = True
                        new_course.save()

        instance.save()
        return instance

    def create(self, validated_data):
        courses = validated_data.pop("courses")
        validated_data["user"] = self.context["request"].user
        semester = Semester.objects.create(**validated_data)
        for course in courses:
            exisiting_courses = Course.objects.filter(code=course["code"], name=course["name"], user=self.context["request"].user)
            # all courses with this code that exist in the audit should be updated
            if exisiting_courses:
                for existing_course in exisiting_courses:
                    existing_course.inProgress = True
                    existing_course.credits = course["credits"]
                    existing_course.semester = semester
                    existing_course.save()
            else:
                # Course is not specified in audit, therefore we manually add it to specified category
                category = course["category"]
                if category != "Auto":
                    course["category"] = Category.objects.get(name=category, user=self.context["request"].user)
                    course["user"] = self.context["request"].user
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
