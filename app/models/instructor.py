from sqlalchemy import Column, Sequence, Integer, Text
from app.database import Base

class InstructorModel(Base):
    __tablename__ = "instructor"

    id = Column(Integer, Sequence("instructor_id_seq"), primary_key=True, autoincrement=True, index=True)
    instructor_onyen = Column(Text, nullable=False, unique=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)