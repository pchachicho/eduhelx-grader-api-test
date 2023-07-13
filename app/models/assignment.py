from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, Text, DateTime,
    func
)
from sqlalchemy.orm import relationship
from app.database import Base

class AssignmentModel(Base):
    __tablename__ = "assignment"

    id = Column(Integer, Sequence("assignment_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False)
    git_remote_url = Column(Text, nullable=False)
    revision_count = Column(Integer, default=0)
    created_date = Column(DateTime, default=func.current_timestamp())
    released_date = Column(DateTime)
    last_modified_date = Column(DateTime, default=func.current_timestamp())
    due_date = Column(DateTime, nullable=False)