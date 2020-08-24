from django.db import models
from django.contrib.auth.models import User

# Create your models here.

TYPES = [("Major", "Major"), ("Minor", "Minor")]


class Program(models.Model):
    label = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name="programs", on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=200)
    program = models.ForeignKey(Program, related_name="categories", on_delete=models.CASCADE)


class Course(models.Model):
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    credits = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name="courses", on_delete=models.CASCADE)


class Semester(models.Model):
    number = models.PositiveIntegerField()
    term = models.CharField(max_length=200)
    courses = models.ManyToManyField(Course, related_name="semesters")
    user = models.ForeignKey(User, related_name="semesters", on_delete=models.CASCADE)

