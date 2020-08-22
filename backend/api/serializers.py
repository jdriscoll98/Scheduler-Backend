from rest_framework import serializers
from .models import Program, TYPES
from django.contrib.auth.models import User


class ProgramSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Program
        fields = ["id", "college", "type", "subject", "user"]


class UserSerializer(serializers.ModelSerializer):
    programs = serializers.PrimaryKeyRelatedField(many=True, queryset=Program.objects.all())  # reverse relationship

    class Meta:
        model = User
        fields = ["id", "username", "snippets"]
