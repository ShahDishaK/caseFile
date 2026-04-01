from sqlalchemy import Column, Integer,DateTime, ForeignKey
from datetime import datetime
from config.db_config import Base
from datetime import datetime


class BlockedClients(Base):
    __tablename__="blockedClients"

    id = Column(Integer, primary_key=True, index=True)
    clientId=Column(Integer, ForeignKey('clients.id'), nullable=False)
    lawyerId=Column(Integer, ForeignKey('lawyer.id'), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
