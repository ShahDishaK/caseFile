# Importing libraries
from dtos.auth_models import UserModel
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import  get_db
from fastapi import APIRouter,Depends
from starlette import status 
from models.users_table import UserRole
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.courtsession_models import SessionModel as CreatSessionRequest
from controllers.courtSession_controller import CourtSessionController

session=APIRouter(
    prefix='/sessions',
    tags=['session']
)

@session.post("/session", status_code=status.HTTP_201_CREATED)
async def create_document(create_session_request: CreatSessionRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.LAWYER],user) 
    return CourtSessionController.create_document(create_session_request,user,db)

@session.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.LAWYER],user) 
    return CourtSessionController.read_all(user,db)