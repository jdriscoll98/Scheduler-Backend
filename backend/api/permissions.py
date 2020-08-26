from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Profile
from django.shortcuts import get_object_or_404


class IsLoggedIn(BasePermission):
    def has_permission(self, request, view):
        if not request.data.get("token"):
            return False
        profile = get_object_or_404(Profile, token=request.data["token"])
        return profile.user.is_authenticated
