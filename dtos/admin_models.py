from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class AdminModel(BaseModel):
    email:EmailStr
    password:str
    name: str
    firstName: str
    lastName: str
    phoneNumber: constr(regex="^[0-9]{10}$")
    address: Optional[str]=None
    gender: str