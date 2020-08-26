from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

# Create your models here.

TYPES = [("Major", "Major"), ("Minor", "Minor")]


class Program(models.Model):
    label = models.CharField(max_length=200)
    overall_progress = models.DecimalField(decimal_places=2, max_digits=6)
    met_groups = models.IntegerField()
    number_of_requirements = models.IntegerField()
    user = models.ForeignKey(User, related_name="programs", on_delete=models.CASCADE)

    def __str__(self):
        return self.label


class Category(models.Model):
    name = models.CharField(max_length=200)
    completed = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=500)
    percent_complete = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    program = models.ForeignKey(Program, related_name="categories", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    credits_required = models.DecimalField(decimal_places=2, max_digits=4)
    credits_towards = models.DecimalField(decimal_places=2, max_digits=4)
    passed = models.BooleanField(default=False)
    inProgress = models.BooleanField(default=False)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name="courses", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category} - {self.code}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(verbose_name="token", default=uuid4, editable=False)
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Semester(models.Model):
    number = models.PositiveIntegerField()
    term = models.CharField(max_length=200)
    courses = models.ManyToManyField(Course, related_name="semesters")
    profile = models.ForeignKey(Profile, related_name="semesters", on_delete=models.CASCADE)

