from fastapi import (
    Header,
    HTTPException
)

from jose import jwt

from database.connection import (
    SessionLocal
)

from database.models import (
    User
)

SECRET_KEY = "supersecretkey"

ALGORITHM = "HS256"


def get_current_user(

    Authorization: str = Header(
        default=None
    )

):

    if not Authorization:

        raise HTTPException(

            status_code=401,

            detail="Missing token"

        )

    try:

        token = Authorization.replace(

            "Bearer ",

            ""

        )

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )

        user_id = payload.get(
            "user_id"
        )

        db = SessionLocal()

        user = db.query(User).filter(

            User.id == user_id

        ).first()

        if not user:

            raise HTTPException(

                status_code=401,

                detail="User not found"

            )

        return user

    except:

        raise HTTPException(

            status_code=401,

            detail="Invalid token"

        )