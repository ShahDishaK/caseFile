from typing import Optional
from pydantic import BaseModel,constr,EmailStr

class StaffModel(BaseModel):
    email: EmailStr
    password: str
    companyId:Optional[int]=None
    name: str
    firstName:str
    lastName:str
    phoneNumber: Optional[constr(regex="^[0-9]{10}$")]
    gender:str
    address: Optional[str] = None
    caseId :Optional[int]=None

class UpdateStaffRequest(BaseModel):
    name: Optional[str] = None
    firstName:Optional[str] = None
    lastName:Optional[str] = None
    phoneNumber: Optional[constr(regex="^[0-9]{10}$")]=None
    gender:Optional[str] = None
    address: Optional[str] = None
    user_id :Optional[int]=None
    caseId :Optional[int]=None
    lawyerId:Optional[int]=None
    isBlocked:Optional[int]=None
    companyId:Optional[int]=None
