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

#to create a job
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

#to get all jobs that are stored
@app.get("/api/jobs/all")
async def get_all_jobs(db:db_dependency):
    db_jobs = db.query(models.Jobs).all()
    if not db_jobs:
        raise HTTPException(status_code= 404, detail = "No Jobs Found")
    return db_jobs


#to get a specific job through id
@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int, db: db_dependency):
    db_job = db.query(models.Jobs).filter(models.Jobs.job_id == job_id).first()
    if not db_job:
        raise HTTPException(status_code= 404, detail = "Job not found")
    return db_job

#to update a job
@app.put("/api/jobs/{job_id}")
async def update_job(job_id: int, model: Model, db: db_dependency):
    db_job = db.query(models.Jobs).filter(models.Jobs.job_id == job_id).first()

    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    db_job.job_name = model.job_name
    db_job.job_description = model.job_description
    db_job.job_command = model.job_command
    db_job.job_scheduled_time = model.job_scheduled_time
    db_job.job_status = model.job_status

    db.commit()
    db.refresh(db_job)
    return db_job

#to delete a job
@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id:int, db: db_dependency):
    db_job = db.query(models.Jobs).filter(models.Jobs.job_id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(db_job)
    db.commit()

    return {"message" : "Job deleted"}
