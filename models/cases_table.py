from sqlalchemy import Column, Integer,Date, String, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
from config.db_config import Base
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    closed = "closed"
    open = "open"

class CaseType(str, Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    FAMILY = "family"
    CORPORATE = "corporate"
    LABOR = "labor"
    PROPERTY = "property"
    TAX = "tax"
    CONSUMER = "consumer"
    IMMIGRATION = "immigration"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    BANKRUPTCY = "bankruptcy"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"

class Cases(Base):
    __tablename__   ="cases"

    id = Column(Integer, primary_key=True, index=True)
    caseNumber = Column(Integer, nullable=False,unique=True)
    title = Column(String(255), nullable=False)
    type=Column(SQLEnum(CaseType),nullable=False)
    description = Column(String(255), nullable=False)
    caseStage=Column(String(50), nullable=False)
    caseCity=Column(String(50), nullable=False)
    status=Column(SQLEnum(CaseStatus), nullable=False)   
    caseClosedDate=Column(Date, nullable=True,default=None)
    clientId=Column(Integer, ForeignKey('clients.id'), nullable=True)
    lawyerId=Column(Integer, ForeignKey('lawyers.id'), nullable=True)
    isDeleted=Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
