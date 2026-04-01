from typing import Optional
from pydantic import BaseModel
from datetime import date

class TaskModel(BaseModel):
    title :str
    description:str
    caseId:int
    priority:str
    dueDate:Optional[date]=None

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    caseId: Optional[int] = None
    assignedTo: Optional[int] = None
    priority: Optional[str] = None  
    companyId:Optional[int]=None
