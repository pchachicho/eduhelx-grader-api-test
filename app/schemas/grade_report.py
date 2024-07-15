from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class GradeReportSchema(BaseModel):
    id: int
    average: float
    median: float
    minimum: float
    maximum: float
    stdev: float
    scores: list[float]
    total_points: float
    num_passing: int
    num_submitted: int

    master_notebook_content: str
    otter_config_content: str
    
    created_date: datetime

    assignment_id: int

    class Config:
        orm_mode = True

class SubmissionGradeSchema(BaseModel):
    score: float
    total_points: float
    comments: Optional[str]