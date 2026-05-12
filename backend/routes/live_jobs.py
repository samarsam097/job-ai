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

        similarity = float(

            1 / (
                1 + distances[0][i]
            )

        )

        match_percentage = float(

            round(

                min(
                    100,
                    similarity * 160
                ),

                2
            )

        )

        # -----------------------------
        # BOOSTS
        # -----------------------------

        if role.lower() in (
            matched_job.title or ""
        ).lower():

            match_percentage += 15

        if country != "all":

            if target_country in (
                matched_job.location or ""
            ).lower():

                match_percentage += 10

        match_percentage = min(
            100,
            match_percentage
        )

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
            float(match_percentage)

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