from django.db import models
from django.contrib.auth.models import User

# Create your models here.

TYPES = [("Major", "Major"), ("Minor", "Minor")]


class Program(models.Model):
    college = models.CharField(max_length=200)
    type = models.CharField(choices=TYPES, default="Major", max_length=100)
    subject = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
