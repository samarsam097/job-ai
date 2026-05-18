import scheduler
from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)


from routes.auth import (
    router as auth_router
)

from routes.live_jobs import (
    router as live_jobs_router
)

from routes.saved_jobs import (
    router as saved_jobs_router
)

# Create FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes

app.include_router(
    auth_router
)


app.include_router(
    live_jobs_router
)

app.include_router(
    saved_jobs_router
)