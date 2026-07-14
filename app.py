from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Annotated
from database import engine, sessionLocal
from sqlalchemy.orm import Session
import models


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class Model(BaseModel):
    job_name: str
    job_description: str | None = None
    job_command: str
    job_scheduled_time: datetime
    job_status: Literal["start", "pause", "end"]

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/api/jobs")
async def create_job(model: Model, db: db_dependency):

    db_jobs = models.Jobs(job_name=model.job_name,
                          job_description=model.job_description,
                          job_command=model.job_command,
                          job_scheduled_time=model.job_scheduled_time,
                          job_status=model.job_status)

    db.add(db_jobs)
    db.commit()
    db.refresh(db_jobs)

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int, db: db_dependency):
    db_job = db.query(models.Jobs).filter(models.Jobs.job_id == job_id).first()
    if not db_job:
        raise HTTPException(status_code= 404, detail = "Job not found")
    return db_job