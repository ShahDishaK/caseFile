from typing import Optional
from pydantic import BaseModel,constr

class CompanyModel(BaseModel):
    name :str
    Address:str
    phoneNumber:Optional[constr(regex="^[0-9]{10}$")]
    email:str

class UpdateCompanyRequest(BaseModel):
    name:Optional[str]=None
    Address:Optional[str]=None
    phoneNumber:Optional[constr(regex="^[0-9]{10}$")]=None
    email:Optional[str]=None