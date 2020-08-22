from rest_framework import serializers
from .models import Program, TYPES
from django.contrib.auth.models import User


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "college", "type", "subject", "user"]

