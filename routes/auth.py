from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from passlib.context import CryptContext
from config.db_config import  get_db
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from controllers.auth_controller import AuthController

auth= APIRouter(prefix='/auth',tags=['Auth'])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

@auth.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return AuthController.login_for_access_token(form_data,db)