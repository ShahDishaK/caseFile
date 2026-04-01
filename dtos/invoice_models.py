from enum import Enum
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class InvoiceStatus(str, Enum):
    pending = "pending"
    paid = "paid"


class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class InvoiceModel(BaseModel):
    totalHours: Decimal
    totalAmount: Decimal 
    clientId: int
    caseId: int
    companyId: int
    
class UpdateInvoiceRequest(BaseModel):
    totalHours: Optional[Decimal] = None
    totalAmount: Optional[Decimal] = None
    clientId: Optional[int] = None
    caseId: Optional[int] = None
    companyId: Optional[int] = None
    lawyerId: Optional[int] = None