from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Enum as SQLEnum, String
from datetime import datetime
from config.db_config import Base
from enum import Enum


class InvoiceStatus(str, Enum):
    pending = "pending"
    paid = "paid"


class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    totalAmount = Column(Numeric(10, 2), nullable=True)
    totalHours = Column(Numeric(10, 2), nullable=True)
    status = Column(SQLEnum(InvoiceStatus), nullable=True)
    caseId = Column(Integer, ForeignKey('cases.id'), nullable=False)
    clientId = Column(Integer, ForeignKey('clients.id'), nullable=False)
    lawyerId = Column(Integer, ForeignKey('lawyers.id'), nullable=False)
    companyId = Column(Integer, ForeignKey('companies.id'), nullable=False)
    stripeSessionId = Column(String(255), nullable=True)
    stripePaymentIntentId = Column(String(255), nullable=True)
    paymentStatus = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending)
    paymentMethod = Column(String(50), nullable=True)
    paidAt = Column(DateTime, nullable=True)
    isDeleted=Column(Integer,nullable=False,default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)