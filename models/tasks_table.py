from sqlalchemy import Column, Integer,Date, String, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
from config.db_config import Base
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    OVERDUE = "overdue"
    COMPLETED = "completed"

class Tasks(Base):
    __tablename__="tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    caseId=Column(Integer,ForeignKey('cases.id'), nullable=True)
    assignedTo=Column(Integer,ForeignKey('users.id'), nullable=True)
    priority=Column(String,nullable=True)
    status=Column(SQLEnum(TaskStatus), nullable=False)
    dueDate=Column(Date,nullable=True)
    isDeleted=Column(Integer,nullable=False,default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
