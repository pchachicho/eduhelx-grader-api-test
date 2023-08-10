from sqlalchemy import Column, Sequence, Integer, Text
from app.database import Base

class UserModel(Base):
    __tablename__ = "user"
    
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, autoincrement=True, index=True)
    user_type = Column(Text, nullable=False)

    onyen = Column(Text, nullable=False, unique=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)

    __mapper_args__ = {"polymorphic_on": "user_type"}