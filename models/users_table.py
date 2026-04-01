from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from enum import Enum
from datetime import datetime
from config.db_config import Base
from datetime import datetime

class UserRole(str, Enum):
    LAWYER = "lawyer"
    ADMIN = "admin"
    STAFF = "staff"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name=Column(String(255), nullable=False)
    firstName=Column(String(255))
    lastName=Column(String(255))
    email = Column(String(255), nullable=False,unique=True)
    phoneNumber=Column(String(15),nullable=True,unique=True)
    password = Column(String(255), nullable=True)
    address=Column(String(255), nullable=True)
    gender=Column(String(100),nullable=True)
    role = Column(SQLEnum(UserRole), nullable=True)
    companyId =  Column(Integer, ForeignKey('companies.id'),nullable=True)
    isDeleted=Column(Boolean,default=False)
    isBlocked = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

