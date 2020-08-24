import json
import re

f = open("data-raw.json")

data = json.load(f)

career = data["careers"][0]

planGroups = career["planGroups"]

majorGroup = planGroups[1]

program = {}

program["label"] = majorGroup[0]["title"]
program["categories"] = []
for group in majorGroup[3:]:
    requirements = group.get("requirements")
    if requirements:
        for requirement in requirements:
            subRequirements = requirement.get("subRequirements")
            if subRequirements:
                category = {}
                category["name"] = requirement["title"]
                category["courses"] = []
                for subreq in subRequirements:
                    course = {}
                    title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
                    if re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8]):
                        course["name"] = title.group(0)
                        course["code"] = subreq["title"][:7]
                        course["credits"] = subreq["unitsRequired"]
                        course["group"] = subreq["requirementGroup"]
                        category["courses"].append(course)
                    else:
                        elective_credits = int(float(subreq["unitsRequired"]))
                        if elective_credits > 0:
                            course = {}
                            course["name"] = subreq["title"]
                            course["code"] = "Elective(s)"
                            course["credits"] = subreq["unitsRequired"]
                            course["group"] = subreq["requirementGroup"]
                            category["courses"].append(course)
                if category["courses"]:
                    program["categories"].append(category)

print(program)
