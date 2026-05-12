import requests

def fetch_remoteok_jobs():

    url = "https://remoteok.com/api"

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    data = response.json()

    jobs = []

    for job in data[1:]:

        jobs.append({
            "title": job.get("position", ""),
            "company": job.get("company", ""),
            "location": "Remote",
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": "remoteok"
        })

    return jobs