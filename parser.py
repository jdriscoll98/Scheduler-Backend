import json
import re

f = open("data-raw.json")

data = json.load(f)


majorGroup = data["careers"][0]["planGroups"][1]

program = {}

program["label"] = majorGroup[0]["title"]
program["overall_progress"] = data["careers"][0]["progressValue"] * 100
program["met_groups"] = data["careers"][0]["numberOfMet"] + data["careers"][0]["numberOfInProgress"]
program["num_of_requirements"] = data["careers"][0]["numberOfRequirements"]
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
                category["completed"] = 0
                category["description"] = requirement["description"]
                for subreq in subRequirements:
                    course = {}
                    title = re.search("(?<= - )[A-Za-z0-9. ]+", subreq["title"])
                    if re.match("^[A-Z]{3} ?[0-9]{4}[A-Z]{0,1} ?$", subreq["title"][:8]):
                        course["name"] = subreq["title"][10:]
                        course["code"] = subreq["title"][:8]
                        course["credits_required"] = subreq["unitsRequired"]
                        course["credits_towards"] = subreq["unitsUsed"]
                        course["passed"] = subreq["met"]
                        course["inProgress"] = subreq["inProgress"]
                        course["description"] = subreq["description"]
                        if subreq["met"] or subreq["inProgress"]:
                            category["completed"] += 1
                        course["group"] = subreq["requirementGroup"]
                        category["courses"].append(course)
                    else:
                        elective_credits = int(float(subreq["unitsRequired"]))
                        if elective_credits > 0:
                            course = {}
                            course["name"] = subreq["title"]
                            course["code"] = "Elective(s)"
                            course["credits_required"] = subreq["unitsRequired"]
                            course["credits_towards"] = subreq["unitsUsed"]
                            category["percent_complete"] = min((float(subreq["unitsUsed"]) / float(subreq["unitsRequired"])) * 100, 100)
                            course["group"] = subreq["requirementGroup"]
                            course["passed"] = subreq["met"]
                            course["description"] = subreq["description"]
                            category["courses"].append(course)

                if category["courses"]:
                    if not category.get("percent_complete"):
                        category["percent_complete"] = min((category["completed"] / len(category["courses"])) * 100, 100)
                    program["categories"].append(category)

