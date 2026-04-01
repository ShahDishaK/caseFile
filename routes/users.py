# Importing libraries
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import  get_db
from dtos.user_models import UpdateUserProfile, UserVerification,ForgotPassword
from dtos.auth_models import UserModel
from typing_extensions import Annotated
from fastapi import APIRouter,Depends
from starlette import status 
from models.users_table import UserRole
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from controllers.user_controller import UserController

router=APIRouter(
    prefix='/users',
    tags=['users']
)

user_dependency=Annotated[dict,Depends(TokenHelper.get_current_user)]

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user) 
    return UserController.read_all(user,db)

@router.get("/profile",status_code=status.HTTP_200_OK)
async def get_user(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    return UserController.get_user(user,db)

@router.put("/change_password",status_code=status.HTTP_200_OK)
async def change_password(user_verification: UserVerification,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    return UserController.change_password(user_verification,user,db)

@router.put("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(user_verification: ForgotPassword, db: Session = Depends(get_db)):
    return UserController.forgot_password(user_verification,db)

@router.patch   ("/updateProfile", status_code=status.HTTP_200_OK)
async def update_profile(update_user_profile: UpdateUserProfile,user: UserModel = Depends(TokenHelper.get_current_user), db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    return UserController.update_profile(update_user_profile,user,db)