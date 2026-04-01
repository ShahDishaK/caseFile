from enum import Enum
from typing import Optional
from pydantic import BaseModel

class CaseStatus(str, Enum):
    closed = "closed"
    open = "open"
    

class CaseStatusHistoryModel(BaseModel):
    caseId :int
    oldStatus :CaseStatus 
    newStatus:CaseStatus
      
class UpdateCaseStatusHistoryRequest(BaseModel):
    oldStatus: Optional[CaseStatus] = None
    newStatus: Optional[CaseStatus] = None
   