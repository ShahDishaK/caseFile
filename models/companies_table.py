from sqlalchemy import Column,Integer, String, DateTime
from datetime import datetime
from config.db_config import Base
from datetime import datetime

class Companies(Base):
    __tablename__="companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    Address = Column(String(255), nullable=False)
    phoneNumber=Column(String(15), nullable=False,unique=True)
    email=Column(String(30),nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
