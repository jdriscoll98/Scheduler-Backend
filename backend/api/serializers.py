from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


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

