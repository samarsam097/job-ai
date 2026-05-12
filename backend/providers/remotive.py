import requests

def fetch_remotive_jobs(role):

    url = "https://remotive.com/api/remote-jobs"

    response = requests.get(url)

    data = response.json()

    jobs = []

    for job in data["jobs"]:

        jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": "Remote",
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": "remotive"
        })

    return jobs