from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from datetime import datetime
from config.db_config import Base
from datetime import datetime

class Lawyers(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    specialization = Column(String(255), nullable=False)
    isBlocked = Column(Integer, default=0)
    isDeleted=Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
