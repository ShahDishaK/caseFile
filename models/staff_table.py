from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from datetime import datetime
from config.db_config import Base
from datetime import datetime

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    caseId = Column(Integer, ForeignKey('cases.id'), nullable=True)
    lawyerId= Column(Integer,ForeignKey('lawyers.id'), nullable=True)
    taskId= Column(Integer,ForeignKey('tasks.id'),nullable=True)
    isBlocked = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
