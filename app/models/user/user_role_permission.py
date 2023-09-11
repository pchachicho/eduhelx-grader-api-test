from sqlalchemy import Column, Sequence, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from app.database import Base

class UserRolePermissionModel(Base):
    __tablename__ = "user_role_permission"

    id = Column(Integer, Sequence("user_role_id_seq"), primary_key=True, autoincrement=True, index=True)
    role_name = Column(Text, ForeignKey("user_role.name"))
    permission_name = Column(Text, ForeignKey("user_permission.name"))

    __table_args__ = (UniqueConstraint("role_name", "permission_name"),)