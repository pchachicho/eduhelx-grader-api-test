import enum
from sqlalchemy import Column, Sequence, Integer, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserType(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"

class UserModel(Base):
    __tablename__ = "user_account"
    
    id = Column(Integer, Sequence("user_account_id_seq"), primary_key=True, autoincrement=True, index=True)
    user_type = Column(Enum(UserType), nullable=False)

    onyen = Column(Text, nullable=False, unique=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    
    role_name = Column(Text, ForeignKey("user_role.name"), nullable=False)
    role = relationship("UserRoleModel", foreign_keys="UserModel.role_name")

    __mapper_args__ = {
        "polymorphic_on": "user_type",
        "polymorphic_identity": "user"
    }