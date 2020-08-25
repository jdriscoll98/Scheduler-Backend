from .models import Program, Category, Course
import re


def parse_audit(data, user):
    majorGroup = data["careers"][0]["planGroups"][1]
    progress = round(data["careers"][0]["progressValue"] * 100, 2)
    program = Program.objects.create(
        user=user,
        label=majorGroup[0]["title"],
        overall_progress=progress,
        met_groups=data["careers"][0]["numberOfMet"] + data["careers"][0]["numberOfInProgress"],
        number_of_requirements=data["careers"][0]["numberOfRequirements"],
    )
    program.save()
    for group in majorGroup[3:]:
        requirements = group.get("requirements")
        if requirements:
            for requirement in requirements:
                subrequirements = requirement.get("subRequirements")
                if subrequirements:
                    category = Category.objects.create(
                        name=requirement["title"], completed=0, description=requirement["description"], program=program
                    )
                    category.save()
                    for subreq in subrequirements:
                        title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
                        if re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8]):
                            course = Course.objects.create(
                                name=subreq["title"][10:],
                                code=subreq["title"][:8],
                                credits_required=subreq["unitsRequired"],
                                credits_towards=subreq["unitsUsed"],
                                passed=subreq["met"],
                                inProgress=subreq["inProgress"],
                                description=subreq["description"],
                                category=category,
                            )
                            course.save()
                            if subreq["met"] or subreq["inProgress"]:
                                category.completed += 1
                                category.save()
                        else:
                            elective__credits = float(subreq["unitsRequired"])
                            if elective__credits >= 1:
                                course = Course.objects.create(
                                    name=subreq["title"],
                                    code="Elective(s)",
                                    credits_required=subreq["unitsRequired"],
                                    credits_towards=subreq["unitsUsed"],
                                    passed=subreq["met"],
                                    description=subreq["description"],
                                    category=category,
                                )
                                course.save()
                                category.percent_complete = min((float(subreq["unitsUsed"]) / float(subreq["unitsRequired"])) * 100, 100)
                                category.save()
                    if len(category.courses.all()) > 0:
                        if not category.percent_complete:
                            category.percent_complete = min((category.completed / len(category.courses.all())) * 100, 100)
                            category.save()
                    else:
                        category.delete()
    return program
