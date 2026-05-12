async function uploadResume() {

    const fileInput =
        document.getElementById("resumeInput");

    const file =
        fileInput.files[0];

    const role =
        document.getElementById("role").value;

    const country =
        document.getElementById("country").value;

    const resultsDiv =
        document.getElementById("results");

    if (!file) {

        resultsDiv.innerHTML = `
            <p>Please upload a resume first.</p>
        `;

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "role",
        role
    );

    formData.append(
        "country",
        country
    );

    resultsDiv.innerHTML = `
        <p>Finding best matching jobs...</p>
    `;

    try {

        const response =
            await fetch(

                "http://127.0.0.1:8000/live-job-search",

                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        console.log(data);

        resultsDiv.innerHTML = "";

        if (!Array.isArray(data)) {

            resultsDiv.innerHTML = `
                <p>Invalid backend response.</p>
            `;

            return;
        }

        if (data.length === 0) {

            resultsDiv.innerHTML = `
                <p>No matching jobs found.</p>
            `;

            return;
        }

        data.forEach(job => {

            resultsDiv.innerHTML += `

                <div class="job-card">

                    <h3>
                        ${job.title}
                    </h3>

                    <p>
                        ${job.company}
                    </p>

                    <p>
                        ${job.location}
                    </p>
                    <p class="source">
    Source:
    ${job.source}
</p>

                    <p>
                        ${(job.description || "No description")
    .slice(0, 300)}...
                    </p>

                    <p>
                        Match Score:
                        ${job.match_percentage}%
                    </p>

                    <a
                        href="${job.url}"
                        target="_blank"
                    >
                        Apply Now
                    </a>

                </div>

            `;
        });

    } catch(error) {

        console.error(error);

        resultsDiv.innerHTML = `
            <p>Something went wrong.</p>
        `;
    }
}