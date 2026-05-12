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