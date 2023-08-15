from sqlalchemy import Column, Sequence, Integer, Text
from app.database import Base

class UserPermissionModel(Base):
    __tablename__ = "user_permission"

    id = Column(Integer, Sequence("user_permission_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False, unique=True)