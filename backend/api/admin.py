from django.contrib import admin
from .models import Program, Category, Course

# Register your models here.
admin.site.register(Program)
admin.site.register(Category)
admin.site.register(Course)
