from sqlalchemy import Column, Integer,DateTime, ForeignKey
from datetime import datetime
from config.db_config import Base
from datetime import datetime


class BlockedLawyers(Base):
    __tablename__="blockedLawyers"

    id = Column(Integer, primary_key=True, index=True)
    lawyerId=Column(Integer, ForeignKey('lawyer.id'), nullable=False)
    adminId=Column(Integer, ForeignKey('users.id'), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
