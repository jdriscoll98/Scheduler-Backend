from .models import Program, Category, Course
from django.shortcuts import get_object_or_404
import re


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
                        category = Category.objects.create(name=requirement["title"], description=requirement["description"], program=program)
                        category.save()
                        for subreq in subrequirements:
                            title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
                            if re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8]):
                                course = Course.objects.create(
                                    name=subreq["title"][10:],
                                    code=subreq["title"][:8].strip(),
                                    credits_required=subreq["unitsRequired"],
                                    credits=subreq["unitsUsed"],
                                    passed=subreq["met"],
                                    inProgress=subreq["inProgress"],
                                    description=subreq["description"],
                                    category=category,
                                )
                                course.save()
                            else:
                                elective_credits = float(subreq["unitsRequired"])
                                if elective_credits >= 1:
                                    course = Course.objects.create(
                                        name=subreq["title"],
                                        code="Elective(s)",
                                        credits_required=subreq["unitsRequired"],
                                        credits=subreq["unitsUsed"],
                                        passed=subreq["met"],
                                        description=subreq["description"],
                                        category=category,
                                    )
                                    course.save()
                                    category.save()
                        if len(category.courses.all()) < 0:
                            category.delete()
        programs.append(program)
    return programs
