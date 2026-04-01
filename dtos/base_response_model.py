# Importing Libraries
from pydantic import BaseModel
from typing import Any, Optional

class BaseResponseModel(BaseModel):
    data: Any
    message: Optional[str] = None

class BaseErrorModel(BaseModel):
    data: Optional[Any] = None
    error: Optional[str] = None
