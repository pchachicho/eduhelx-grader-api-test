from sqlalchemy import Column, Sequence, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.database import Base

class UserRoleModel(Base):
    __tablename__ = "user_role"

    id = Column(Integer, Sequence("user_role_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False, unique=True)
    role_permissions = relationship("UserRolePermissionModel", back_populates="role")
    permissions = association_proxy("role_permissions", "permission")