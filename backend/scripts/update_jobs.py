import sys

import os
from database.models import SavedJob

sys.path.append(

    os.path.dirname(

        os.path.dirname(

            os.path.abspath(__file__)

        )

    )

)

import re
import os
import pickle
import faiss
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

from database.connection import (
    SessionLocal
)

from database.models import Job

from providers.aggregator import (
    fetch_all_jobs
)

# -----------------------------
# LOAD MODEL
# -----------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------
# FETCH JOBS
# -----------------------------

print("Fetching jobs...")

jobs = fetch_all_jobs(
    "software engineer",
    "all"
)

print(
    f"Fetched {len(jobs)} jobs"
)

# -----------------------------
# DEDUPLICATION
# -----------------------------

unique_jobs = []

seen = set()

for job in jobs:

    unique_key = (

        job.get(
            "title",
            ""
        ).lower()

        +

        job.get(
            "company",
            ""
        ).lower()

    )

    if unique_key in seen:
        continue

    seen.add(unique_key)

    unique_jobs.append(job)

print(
    f"{len(unique_jobs)} jobs after deduplication"
)

# -----------------------------
# DATABASE
# -----------------------------

db = SessionLocal()

print("Deleting old saved jobs...")

db.query(SavedJob).delete()

db.commit()

print("Deleting old jobs...")

db.query(Job).delete()

db.commit()

# -----------------------------
# CLEAN + COLLECT
# -----------------------------

clean_jobs = []

embedding_texts = []

print(
    "Cleaning jobs..."
)

for job in unique_jobs:

    raw_description = job.get(
        "description",
        ""
    )

    clean_description = re.sub(

        "<.*?>",

        "",

        raw_description

    )

    clean_description = (
        clean_description
        .replace("\n", " ")
        .strip()
    )

    # -----------------------------
    # FILTER BAD JOBS
    # -----------------------------

    if len(clean_description) < 50:
        continue

    if not job.get("title"):
        continue

    if not job.get("url"):
        continue

    # -----------------------------
    # EMBEDDING TEXT
    # -----------------------------

    embedding_text = f"""

    {job.get('title', '')}

    {job.get('company', '')}

    {job.get('location', '')}

    {clean_description}

    """

    embedding_texts.append(
        embedding_text
    )

    clean_jobs.append({

        "title": job.get(
            "title",
            ""
        ),

        "company": job.get(
            "company",
            ""
        ),

        "location": job.get(
            "location",
            ""
        ),

        "description":
        clean_description,

        "url": job.get(
            "url",
            ""
        ),

        "source": job.get(
            "source",
            ""
        )
    })

print(
    f"{len(clean_jobs)} clean jobs ready"
)

# -----------------------------
# BATCH EMBEDDINGS
# -----------------------------

print(
    "Creating embeddings..."
)

embeddings = model.encode(

    embedding_texts,

    batch_size=32,

    show_progress_bar=True

)

embeddings = np.array(
    embeddings
).astype("float32")

# -----------------------------
# SAVE JOBS
# -----------------------------

job_ids = []

db_jobs = []

print(
    "Saving jobs to database..."
)

for idx, job in enumerate(clean_jobs):

    db_job = Job(

        title=job["title"],

        company=job["company"],

        location=job["location"],

        description=job["description"],

        url=job["url"],

        source=job["source"]
    )

    db_jobs.append(db_job)

    if (idx + 1) % 50 == 0:

        print(
            f"Prepared {idx + 1} jobs"
        )

# -----------------------------
# SINGLE COMMIT
# -----------------------------

db.add_all(db_jobs)

db.commit()

# -----------------------------
# GET IDS
# -----------------------------

for job in db_jobs:

    db.refresh(job)

    job_ids.append(job.id)

print(
    "Database save complete"
)

# -----------------------------
# CREATE FAISS INDEX
# -----------------------------

print(
    "Creating FAISS index..."
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    embeddings
)

# -----------------------------
# TEMP FILE PATHS
# -----------------------------

temp_index_path = (
    "data/jobs_new.index"
)

temp_ids_path = (
    "data/job_ids_new.pkl"
)

# -----------------------------
# SAVE TEMP FILES
# -----------------------------

faiss.write_index(

    index,

    temp_index_path

)

with open(

    temp_ids_path,

    "wb"

) as f:

    pickle.dump(
        job_ids,
        f
    )

# -----------------------------
# ATOMIC REPLACEMENT
# -----------------------------

os.replace(

    temp_index_path,

    "data/jobs.index"

)

os.replace(

    temp_ids_path,

    "data/job_ids.pkl"

)

print("DONE!")