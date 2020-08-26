from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Count
import json, os

from api.utils import parse_audit

# Create your tests here.
class TestAPI(TestCase):
    def setUp(self):
        self.data = json.load(open("api/tests/data-raw.json"))
        self.user = User.objects.create(username="test-user")

    def test_parse_audit(self):
        program = parse_audit(self.data, self.user)

        self.assertEqual(program.user, self.user)
        self.assertEqual(program.overall_progress, 70.0)
        self.assertEqual(program.met_groups, 7)
        self.assertEqual(program.number_of_requirements, 10)

        self.assertEqual(program.categories.all().count(), 16)

        category = program.categories.get(name="Critical Tracking Courses")

        self.assertEqual(category.percent_complete, 100)

        course = category.courses.get(code="CHM2045 ")

        self.assertEqual(course.name, "General Chemistry or CHM2095 - Chemistry for Engineers 1")
