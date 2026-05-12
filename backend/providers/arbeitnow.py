import requests

def fetch_arbeitnow_jobs():

    jobs = []

    for page in range(1, 11):

        url = f"""
        https://www.arbeitnow.com/api/job-board-api?page={page}
        """

        url = url.strip()

        response = requests.get(url)

        if response.status_code != 200:
            break

        if not response.text.strip():
            break

        try:
            data = response.json()
        except:
            break

        data = response.json()

        for job in data["data"]:

            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "url": job.get("url", ""),
                "source": "arbeitnow"
            })

        print(f"Fetched ArbeitNow page {page}")

    return jobs