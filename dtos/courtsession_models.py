from typing import Optional
from pydantic import BaseModel
from datetime import date, time

class SessionModel(BaseModel):
    sessionDate:date
    sessionTime:time
    courtName:str
    caseId:int
    clientId:int