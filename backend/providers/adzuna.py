import requests

APP_ID = "eb821d8a"

APP_KEY = "8d385253e3af4ac2e1ff662790f8ed61"


def fetch_adzuna_jobs(
    role,
    country
):

    if country == "all":

        countries = [

            "us",

            "gb",

            "de",

            "at",

            "ca",

            "in"

        ]

    else:

        countries = [country]

    jobs = []

    for country_code in countries:

        for page in range(1, 3):

            url = (

                f"https://api.adzuna.com/v1/api/jobs/"

                f"{country_code}/search/{page}"

                f"?app_id={APP_ID}"

                f"&app_key={APP_KEY}"

                f"&results_per_page=20"

                f"&what={role}"

            )

            print(url)

            response = requests.get(url)

            print(
                "Status:",
                response.status_code
            )

            if response.status_code != 200:
                continue

            data = response.json()

            for job in data.get(
                "results",
                []
            ):

                jobs.append({

                    "title": job.get(
                        "title",
                        ""
                    ),

                    "company": job.get(
                        "company",
                        {}
                    ).get(
                        "display_name",
                        ""
                    ),

                    "location": job.get(
                        "location",
                        {}
                    ).get(
                        "display_name",
                        ""
                    ),

                    "url": job.get(
                        "redirect_url",
                        ""
                    )

                })

    return jobs