from sqlalchemy import Column, Integer, String, Text
from database.connection import Base

class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)

    company = Column(String)

    location = Column(String)

    description = Column(Text)

    url = Column(String)

    source = Column(String)

from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    saved_jobs = relationship(
        "SavedJob",
        back_populates="user"
    )


class SavedJob(Base):

    __tablename__ = "saved_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id")
    )

    user = relationship(
        "User"
    )

    job = relationship(
        "Job"
    )