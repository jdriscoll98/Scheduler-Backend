from django.db import models
from django.contrib.auth.models import User


class Program(models.Model):
    label = models.CharField(max_length=200)
    number_of_requirements = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name="programs", on_delete=models.CASCADE)

    def __str__(self):
        return self.label


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    program = models.ForeignKey(Program, related_name="categories", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="categories", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Semester(models.Model):
    number = models.PositiveIntegerField()
    term = models.CharField(max_length=200)
    year = models.CharField(max_length=4)
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, related_name="semesters", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.term + " " + self.year


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    credits = models.IntegerField(default=0)
    credits_required = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    inProgress = models.BooleanField(default=False)
    description = models.CharField(max_length=200, blank=True, default="N/A")
    semester = models.ForeignKey(Semester, related_name="courses", null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, related_name="courses", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="courses", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category} - {self.code}"
