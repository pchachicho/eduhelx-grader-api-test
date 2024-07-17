from sqlalchemy import (
    Column, Sequence,
    Integer, Text, DateTime,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class AssignmentModel(Base):
    __tablename__ = "assignment"

    id = Column(Integer, Sequence("assignment_id_seq"), primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)
    directory_path = Column(Text, nullable=False)
    max_attempts = Column(Integer)
    created_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    available_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    last_modified_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    @hybrid_property
    def is_created(self):
        return self.available_date is not None and self.due_date is not None
