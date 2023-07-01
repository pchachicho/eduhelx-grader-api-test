from sqlalchemy import Column, Sequence, Integer, Text
from app.database import Base

class StudentModel(Base):
    __tablename__ = "student"

    id = Column(Integer, Sequence("student_id_seq"), primary_key=True, autoincrement=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    professor_onyen = Column(Text, nullable=False)