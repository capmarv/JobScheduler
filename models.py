from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base

class Jobs(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String)
    job_description = Column(String)
    job_command = Column(String)
    job_scheduled_time = Column(DateTime)
    job_status = Column(String)

