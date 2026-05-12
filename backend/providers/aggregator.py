from providers.adzuna import (
    fetch_adzuna_jobs
)

from providers.remotive import (
    fetch_remotive_jobs
)

from providers.arbeitnow import (
    fetch_arbeitnow_jobs
)

from providers.themuse import (
    fetch_themuse_jobs
)

from providers.remoteok import (
    fetch_remoteok_jobs
)


def fetch_all_jobs(
    role,
    country
):

    jobs = []

    try:
        jobs.extend(
            fetch_adzuna_jobs(
                role,
                country
            )
        )
    except Exception as e:
        print("Adzuna Error:", e)

    try:
        jobs.extend(
            fetch_remotive_jobs(
                role
            )
        )
    except Exception as e:
        print("Remotive Error:", e)

    try:
        jobs.extend(
            fetch_arbeitnow_jobs()
        )
    except Exception as e:
        print("Arbeitnow Error:", e)

    try:
        jobs.extend(
            fetch_themuse_jobs(
                role
            )
        )
    except Exception as e:
        print("TheMuse Error:", e)

    try:
        jobs.extend(
            fetch_remoteok_jobs()
        )
    except Exception as e:
        print("RemoteOK Error:", e)

    return jobs