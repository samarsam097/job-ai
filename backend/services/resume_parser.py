import re


def extract_section(

    text,

    section_names

):

    lines = text.split("\n")

    extracted = []

    capture = False

    for line in lines:

        clean_line = line.strip().lower()

        if clean_line in section_names:

            capture = True
            continue

        if capture:

            if len(clean_line) < 2:
                continue

            # Stop on next section
            if clean_line in [

                "education",
                "experience",
                "skills",
                "projects",
                "certifications"

            ]:

                break

            extracted.append(line)

    return "\n".join(extracted)


def parse_resume(

    text

):

    text = text.replace("\r", "\n")

    education = extract_section(

        text,

        ["education"]

    )

    experience = extract_section(

        text,

        ["experience"]

    )

    skills = extract_section(

        text,

        ["skills"]

    )

    projects = extract_section(

        text,

        ["projects"]

    )

    certifications = extract_section(

        text,

        ["certifications"]

    )

    return {

        "education":
        education,

        "experience":
        experience,

        "skills":
        skills,

        "projects":
        projects,

        "certifications":
        certifications

    }