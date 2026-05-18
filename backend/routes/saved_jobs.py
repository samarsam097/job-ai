from fastapi import (

    APIRouter,

    Depends

)

from database.connection import (
    SessionLocal
)

from database.models import (

    SavedJob,

    Job

)

from services.dependencies import (
    get_current_user
)


router = APIRouter()


@router.post("/save-job/{job_id}")
def save_job(

    job_id: int,

    current_user = Depends(
        get_current_user
    )

):

    db = SessionLocal()

    existing = db.query(SavedJob).filter(

        SavedJob.user_id == current_user.id,

        SavedJob.job_id == job_id

    ).first()

    if existing:

        return {

            "message":
            "Already saved"

        }

    saved_job = SavedJob(

        user_id=current_user.id,

        job_id=job_id

    )

    db.add(saved_job)

    db.commit()

    return {

        "message":
        "Job saved"
    }


@router.get("/saved-jobs")
def get_saved_jobs(

    current_user = Depends(
        get_current_user
    )

):

    db = SessionLocal()

    saved_jobs = db.query(SavedJob).filter(

        SavedJob.user_id == current_user.id

    ).all()

    results = []

    for saved in saved_jobs:

        job = db.query(Job).filter(

            Job.id == saved.job_id

        ).first()

        if job:

            results.append({

                "id": job.id,

                "title": job.title,

                "company": job.company,

                "location": job.location,

                "url": job.url

            })

    return results