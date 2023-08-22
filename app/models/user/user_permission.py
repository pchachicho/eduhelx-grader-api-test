from sqlalchemy import Column, Sequence, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base

class UserPermissionModel(Base):
    __tablename__ = "user_permission"

    id = Column(Integer, Sequence("user_permission_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False, unique=True)

    roles = relationship(
        "UserRoleModel",
        secondary="user_role_permission",
        back_populates="permissions"
    )