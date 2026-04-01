from typing import Optional
from pydantic import BaseModel
from datetime import date
from enum import Enum

class CaseStatus(str, Enum):
    closed = "closed"
    open = "open"


class CaseModel(BaseModel):
    caseNumber :int
    title :str 
    type:str
    description : str
    status: CaseStatus
    caseClosedDate: Optional[date] = None
    caseStage:str
    caseCity:str
    clientId: Optional[int] = None
   
class UpdateCaseRequest(BaseModel):
    caseNumber: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    staffId: Optional[int] = None
    status: Optional[CaseStatus] = None
    caseCloseDate: Optional[date] = None
    clientId: Optional[int] = None
    lawyerId: Optional[int] = None