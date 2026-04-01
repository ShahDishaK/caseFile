from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from enum import Enum


class UserModel(BaseModel):
    email: EmailStr
    password: str
    companyId:Optional[int]=None
    
class TokenModel(BaseModel):
    access_token: str
    token_type: Optional[str] = 'Bearer'
