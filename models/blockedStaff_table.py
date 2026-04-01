from sqlalchemy import Column, Integer,  DateTime, ForeignKey
from datetime import datetime
from config.db_config import Base
from datetime import datetime


class BlockedStaff(Base):
    __tablename__="blockedStaff"

    id = Column(Integer, primary_key=True, index=True)
    staffId=Column(Integer, ForeignKey('staff.id'), nullable=False)
    lawyerId=Column(Integer, ForeignKey('lawyers.id'), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
