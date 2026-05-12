import requests

def fetch_themuse_jobs(role):

    jobs = []

    for page in range(1, 21):

        url = f"""
        https://www.themuse.com/api/public/jobs?page={page}
        """

        url = url.strip()

        response = requests.get(url)

        data = response.json()

        for job in data["results"]:

            jobs.append({
                "title": job.get("name", ""),
                "company": job.get(
                    "company",
                    {}
                ).get("name", ""),
                "location": ", ".join([
                    loc["name"]
                    for loc in job.get(
                        "locations",
                        []
                    )
                ]),
                "description": job.get(
                    "contents",
                    ""
                ),
                "url": job.get(
                    "refs",
                    {}
                ).get(
                    "landing_page",
                    ""
                ),
                "source": "themuse"
            })

        print(f"Fetched Muse page {page}")

    return jobs