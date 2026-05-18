import pickle
import time
import fitz
import faiss
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from sentence_transformers import (
    SentenceTransformer
)

from database.connection import (
    SessionLocal
)

from database.models import Job

from services.skills import (
    extract_skills
)

from services.resume_parser import (
    parse_resume
)

router = APIRouter()

# -----------------------------
# LOAD MODEL
# -----------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------
# LOAD FAISS INDEX
# -----------------------------

index = faiss.read_index(
    "data/jobs.index"
)

with open(
    "data/job_ids.pkl",
    "rb"
) as f:

    job_ids = pickle.load(f)

# -----------------------------
# COUNTRY MAP
# -----------------------------

country_map = {

    "us": "united states",

    "gb": "united kingdom",

    "de": "germany",

    "at": "austria",

    "ca": "canada",

    "in": "india",

    "all": ""

}


# -----------------------------
# SEARCH ROUTE
# -----------------------------

@router.post("/live-job-search")
async def live_job_search(

    file: UploadFile = File(...),

    role: str = Form(""),

    country: str = Form("all")

):
    start = time.time()

    # -----------------------------
    # DEFAULT ROLE
    # -----------------------------

    if role.strip() == "":

        role = "software engineer"

    # -----------------------------
    # SAVE RESUME
    # -----------------------------

    with open(file.filename, "wb") as f:

        content = await file.read()

        f.write(content)

    # -----------------------------
    # READ PDF
    # -----------------------------

    doc = fitz.open(file.filename)

    resume_text = ""

    for page in doc:

        resume_text += page.get_text()

    parsed_resume = parse_resume(
            resume_text
    )

    resume_skills = extract_skills(

            parsed_resume["skills"]

            +

            "\n"

            +

            parsed_resume["projects"]

    )

        
    
    # -----------------------------
    # RESUME EMBEDDING
    # -----------------------------

    resume_embedding = model.encode(
        resume_text
    ).astype("float32")

    resume_embedding = np.array(
        [resume_embedding]
    )

    # -----------------------------
    # DATABASE
    # -----------------------------

    db = SessionLocal()

    jobs_map = {

        job.id: job

        for job in db.query(Job).all()

    }

    # -----------------------------
    # FILTERED DATA
    # -----------------------------

    filtered_jobs = []

    filtered_embeddings = []

    target_country = country_map.get(
        country,
        ""
    ).lower()

    role_words = role.lower().split()

    # -----------------------------
    # FILTER JOBS
    # -----------------------------

    for idx, job_id in enumerate(job_ids):

        job = jobs_map.get(job_id)

        if not job:
            continue

        job_text = f"""

        {job.title}

        {job.company}

        {job.location}

        {job.description}

        """.lower()

        # -----------------------------
        # ROLE FILTER
        # -----------------------------

        matched = False

        for word in role_words:

            if word in job_text:

                matched = True

                break

        if not matched:
            continue

        # -----------------------------
        # COUNTRY FILTER
        # -----------------------------

        if country != "all":

            if target_country not in (
                job.location or ""
            ).lower():

                continue

        # -----------------------------
        # SAVE FILTERED
        # -----------------------------

        filtered_jobs.append(job)

        embedding = index.reconstruct(
            idx
        )

        filtered_embeddings.append(
            embedding
        )

    # -----------------------------
    # NO RESULTS
    # -----------------------------

    if len(filtered_jobs) == 0:

        return []

    # -----------------------------
    # TEMP FAISS INDEX
    # -----------------------------

    filtered_embeddings = np.array(
        filtered_embeddings
    ).astype("float32")

    dimension = filtered_embeddings.shape[1]

    temp_index = faiss.IndexFlatL2(
        dimension
    )

    temp_index.add(
        filtered_embeddings
    )

    # -----------------------------
    # SEARCH
    # -----------------------------

    k = min(
        20,
        len(filtered_jobs)
    )

    distances, indices = temp_index.search(
        resume_embedding,
        k
    )

    matched_jobs = []

    # -----------------------------
    # BUILD RESULTS
    # -----------------------------

    for i in range(k):

        matched_job = filtered_jobs[
            indices[0][i]
        ]

        job_text = f"""

        {matched_job.title}

        {matched_job.description}

        """.lower()

        job_skills = extract_skills(
            job_text
        )

        matched_skills = list(

            set(resume_skills)

            &

            set(job_skills)

        )           

        skill_score = len(
            matched_skills
        ) * 4

        # -----------------------------
# SEMANTIC SCORE
# -----------------------------

        similarity = float(

            1 / (
                1 + distances[0][i]
            )

        )

        semantic_score = similarity * 100

# -----------------------------
# SKILL SCORE
# -----------------------------

        skill_score = min(

            30,

            len(matched_skills) * 6

        )

# -----------------------------
# TITLE SCORE
# -----------------------------

        title_score = 0

        if role.lower() in (
            matched_job.title or ""
        ).lower():

            title_score = 15

# ------------------------  -----
# COUNTRY SCORE
# -----------------------------

        country_score = 0

        if country != "all":

            if target_country in (
                matched_job.location or ""
            ).lower():

                country_score = 10

        experience_score = 0

        experience_text = parsed_resume[
            "experience"
        ].lower()

        job_text_lower = job_text.lower()

        experience_words = experience_text.split()

        matches = 0

        for word in experience_words:

            if len(word) < 4:
                continue

            if word in job_text_lower:

                 matches += 1

        experience_score = min(
            20,
            matches * 0.5
        )

# -----------------------------
# FINAL WEIGHTED SCORE
# -----------------------------

        final_score = (

            semantic_score * 0.45

            +

            skill_score * 0.25

            +

            experience_score * 0.20

            +

            title_score * 0.07

            +

            country_score * 0.03

        )

        match_percentage = round(
            min(100, final_score),2)
        
        
        # -----------------------------
        # RESULT OBJECT
        # -----------------------------

        matched_jobs.append({

            "title":
            matched_job.title,

            "company":
            matched_job.company,

            "location":
            matched_job.location,

            "description":
            matched_job.description,

            "url":
            matched_job.url,

            "source":
            matched_job.source,

            "match_percentage":
            float(match_percentage),

            "matched_skills":
            matched_skills,

            "experience_score":
            round(experience_score, 2),

        })

    print(
    "Search Time:",
    round(
        time.time() - start,
        2
    ),
    "seconds"
)

    return matched_jobs