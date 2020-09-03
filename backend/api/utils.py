from .models import Program, Category, Course, Semester
from django.shortcuts import get_object_or_404
import re


############## Parsing Utils


def parse_audit(data, user):
    clear_prev_audit(user)
    programs = generatePrograms(data["careers"][0]["planGroups"], user)
    courses_taken = data["careers"][0]["coursesTaken"]
    load_prev_courses(courses_taken, programs[1], user)


def clear_prev_audit(user):
    for program in user.programs.all():
        program.delete()

    for semester in user.semesters.all():
        semester.delete()


def generatePrograms(groups, user):
    programs = []
    for program_group in groups:
        program = Program.objects.create(user=user, label=program_group[0]["title"], number_of_requirements=len(program_group[0]["requirements"]))
        set_up_program(program_group, program, user)
        programs.append(program)
    return programs


def set_up_program(program_group, program, user):
    for group in program_group:
        requirements = group.get("requirements")
        if requirements:
            for requirement in requirements:
                subrequirements = requirement.get("subRequirements")
                if subrequirements:
                    category = Category.objects.create(name=requirement["title"], description=requirement["description"], program=program, user=user)
                    set_up_category(category, subrequirements, program, user)


def is_a_code(subreq):
    return re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8])


def set_up_category(category, subrequirements, program, user):
    for subreq in subrequirements:
        title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
        if is_a_code(subreq):
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
    if len(category.courses.all()) <= 0:
        category.delete()


def load_prev_courses(courses_taken, program, user):
    previous_courses = Category.objects.create(name="Previous Courses", description="Uploaded from degree audit", program=program, user=user)
    semester_number = 1
    for course in courses_taken:
        if course["grade"] != "W":
            term = course["termDescription"].split()[0]
            year = course["termDescription"].split()[1]

            semester, created = Semester.objects.get_or_create(term=term, year=year, user=user, defaults={"number": semester_number})
            if created:
                semester_number += 1

            course = Course.objects.create(
                code=f"{course['subject']}{course['catalogNumber']}",
                credits=float(course["credit"]),
                name=course["courseName"],
                category=previous_courses,
                semester=semester,
                user=user,
                passed=True,
            )


########## Serializer Utils
def set_courses(new_courses, instance, user):

    for course in new_courses:
        # if course.get("id"):
        #     update_existing_course(course, instance)
        # else:
        if course["code"] == "User-Added":
            create_user_added_course(course, instance, user)
        else:
            process_course(course, instance, user)


def update_existing_course(course, instance):
    exisitng_course = Course.objects.get(pk=course["id"])
    exisitng_course.category = Category.objects.get(name=course["category"])
    exisitng_course.semester = instance
    exisitng_course.save()


def create_user_added_course(course, instance, user):
    category = course["category"]
    course["category"] = Category.objects.get(name=category, user=user)
    course["user"] = user
    course["semester"] = instance
    course["inProgress"] = True
    new_course = Course.objects.create(**course)


def process_course(course, instance, user):
    exisiting_courses = Course.objects.filter(code=course["code"], user=user)
    if exisiting_courses:
        # all courses with this code that exist in the audit should be updated
        for existing_course in exisiting_courses:
            existing_course.inProgress = True
            existing_course.credits = course["credits"]
            existing_course.semester = instance
            existing_course.save()
    else:
        # Course is not specified in audit, therefore we manually add it to specified category
        category = course["category"]
        course["category"] = Category.objects.get(name=category, user=user)
        course["user"] = user
        new_course = Course.objects.create(**course)
        new_course.semester = instance
        new_course.inProgress = True
        new_course.save()


def reset_courses(semester):
    for course in semester.courses.all():
        if course.description == "User Added Course":
            course.delete()
        else:
            course.inProgress = False
            course.credits = 0
        course.save()
