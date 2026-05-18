from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from database.connection import (
    SessionLocal
)

from database.models import (
    User
)

from services.auth import (

    hash_password,

    verify_password,

    create_access_token

)


router = APIRouter()


class AuthRequest(BaseModel):

    email: str

    password: str


# -----------------------------
# SIGNUP
# -----------------------------

@router.post("/signup")
def signup(

    data: AuthRequest

):

    db = SessionLocal()

    existing_user = db.query(User).filter(

        User.email == data.email

    ).first()

    if existing_user:

        raise HTTPException(

            status_code=400,

            detail="Email already exists"

        )

    new_user = User(

        email=data.email,

        password=hash_password(
            data.password
        )

    )

    db.add(new_user)

    db.commit()

    return {

        "message":
        "User created successfully"

    }


# -----------------------------
# LOGIN
# -----------------------------

@router.post("/login")
def login(

    data: AuthRequest

):

    db = SessionLocal()

    user = db.query(User).filter(

        User.email == data.email

    ).first()

    if not user:

        raise HTTPException(

            status_code=401,

            detail="Invalid credentials"

        )

    if not verify_password(

        data.password,

        user.password

    ):

        raise HTTPException(

            status_code=401,

            detail="Invalid credentials"

        )

    token = create_access_token({

        "user_id": user.id

    })

    return {

        "access_token": token,

        "token_type": "bearer"

    }