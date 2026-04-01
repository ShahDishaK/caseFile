from sqlalchemy import Column, Integer,  DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
from config.db_config import Base
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    closed = "closed"
    open = "open"
    

class CaseStatusHistories(Base):
    __tablename__="caseStatusHistories"

    id = Column(Integer, primary_key=True, index=True)
    caseId=Column(Integer, ForeignKey('cases.id'), nullable=False)
    oldStatus=Column(SQLEnum(CaseStatus), nullable=True)
    newStatus=Column(SQLEnum(CaseStatus), nullable=True)
    isDeleted=Column(Integer,nullable=False,default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
