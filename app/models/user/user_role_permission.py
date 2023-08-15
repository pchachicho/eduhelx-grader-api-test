from sqlalchemy import Column, Sequence, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from app.database import Base

class UserRolePermissionModel(Base):
    __tablename__ = "user_role_permission"

    id = Column(Integer, Sequence("user_role_id_seq"), primary_key=True, autoincrement=True, index=True)
    role_id = Column(Integer, ForeignKey("user_role.id"))
    permission_id = Column(Integer, ForeignKey("user_permission.id"))

    role = relationship("UserRole", foreign_keys="UserRolePermissionModel.role_id")
    permission = relationship("UserPermission", foreign_keys="UserRolePermissionModel.permission_id")

    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)