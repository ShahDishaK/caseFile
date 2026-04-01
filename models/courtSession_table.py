from sqlalchemy import Column, Date, Time,Integer, String, DateTime, ForeignKey
from datetime import datetime
from config.db_config import Base
from datetime import datetime

class CourtSessions(Base):
    __tablename__="courtSessions"

    id = Column(Integer, primary_key=True, index=True)
    sessionDate=Column(Date, nullable=False)
    sessionTime=Column(Time,nullable=False)
    courtName=Column(String(255), nullable=False)
    caseId=Column(Integer,ForeignKey('cases.id'), nullable=False)
    lawyerId=Column(Integer,ForeignKey('lawyers.id'), nullable=True)
    clientId=Column(Integer,ForeignKey('clients.id'), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
