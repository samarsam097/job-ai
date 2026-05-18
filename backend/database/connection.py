import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


# -----------------------------
# LOAD ENV
# -----------------------------

load_dotenv()

# -----------------------------
# DATABASE URL
# -----------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

print("\nDATABASE URL:")
print(DATABASE_URL)
print()

# -----------------------------
# SQLALCHEMY ENGINE
# -----------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
   

# -----------------------------
# SESSION
# -----------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# BASE
# -----------------------------

Base = declarative_base()