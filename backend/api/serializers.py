from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Profile

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
        profile = Profile.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ("id", "username", "password")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)


class LogoutSerializer(serializers.Serializer):
    token = serializers.UUIDField()
