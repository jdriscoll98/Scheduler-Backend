from rest_framework import serializers
from .models import Semester
from django.contrib.auth.models import User


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        models = Semester
        fields = ["id", "number", "term", "courses"]

