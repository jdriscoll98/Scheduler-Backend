from .models import Program, Category, Course
from django.shortcuts import get_object_or_404
import re
from .serializers import ProgramSerializer, CategorySerializer, CourseSerializer


def parse_audit(data, user):
    programs = []
    for program_group in data["careers"][0]["planGroups"]:

        program = Program.objects.create(user=user, label=program_group[0]["title"], number_of_requirements=len(program_group[0]["requirements"]))
        program.save()
        for group in program_group:
            requirements = group.get("requirements")
            if requirements:
                for requirement in requirements:
                    subrequirements = requirement.get("subRequirements")
                    if subrequirements:
                        category = Category.objects.create(
                            name=requirement["title"], description=requirement["description"], program=program, user=user
                        )
                        category.save()
                        for subreq in subrequirements:
                            title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
                            if re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8]):
                                course = Course.objects.create(
                                    name=subreq["title"][10:].strip(),
                                    code=subreq["title"][:8].replace(" ", ""),
                                    credits_required=float(subreq["unitsRequired"]),
                                    credits=float(subreq["unitsUsed"]),
                                    passed=subreq["met"],
                                    inProgress=subreq["inProgress"],
                                    description="N/A",
                                    category=category,
                                    user=user,
                                )
                                course.save()
                            else:
                                elective_credits = float(subreq["unitsRequired"])
                                if elective_credits >= 1:
                                    course = Course.objects.create(
                                        name=subreq["title"],
                                        code="Current Status",
                                        credits_required=float(subreq["unitsRequired"]),
                                        credits=float(subreq["unitsUsed"]),
                                        passed=subreq["met"],
                                        description=subreq["description"],
                                        category=category,
                                        user=user,
                                    )
                                    course.save()
                                    category.save()
                        if len(category.courses.all()) <= 0:
                            category.delete()
        programs.append(program)
    return programs


def getPrograms(user):
    programs = user.programs.all()
    serialized_programs = []
    for program in programs:
        program_serialized = dict(ProgramSerializer(program).data)
        program_serialized["categories"] = []
        for category in program.categories.all():
            category_serialized = dict(CategorySerializer(category).data)
            category_serialized["courses"] = []
            for course in category.courses.all():
                course_serialized = CourseSerializer(course)
                category_serialized["courses"].append(course_serialized.data)
            program_serialized["categories"].append(category_serialized)
        serialized_programs.append(program_serialized)
    return serialized_programs
