import re


COMMON_SKILLS = [

    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "linux",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "html",
    "css",
    "tailwind",
    "figma",
    "c++",
    "c",
    "c#",
    "go",
    "rust"

]

SKILL_ALIASES = {

    "postgres": "postgresql",

    "postgre": "postgresql",

    "nextjs": "next.js",

    "nodejs": "node.js",

    "tf": "tensorflow",

    "js": "javascript",

    "ts": "typescript"

}


def extract_skills(text):

    text = text.lower()

    found_skills = set()

    for alias, real_skill in (
        SKILL_ALIASES.items()
    ):

        text = text.replace(
        alias,
        real_skill
    )

    for skill in COMMON_SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            found_skills.add(skill)

    return list(found_skills)