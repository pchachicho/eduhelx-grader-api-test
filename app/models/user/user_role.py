from sqlalchemy import Column, Sequence, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base

class UserRoleModel(Base):
    __tablename__ = "user_role"

    id = Column(Integer, Sequence("user_role_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False, unique=True)

    permissions = relationship(
        "UserPermissionModel",
        secondary="user_role_permission",
        back_populates="roles"
    )