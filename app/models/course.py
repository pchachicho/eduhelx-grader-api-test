from __future__ import annotations
from sqlalchemy import Column, Sequence, Integer, Text
from sqlalchemy.orm import Session
from app.database import Base

class CourseModel(Base):
    __tablename__ = "course"

    id = Column(Integer, Sequence("course_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False)
    master_remote_url = Column(Text, nullable=False)