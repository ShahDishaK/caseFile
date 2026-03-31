from controllers.lawyer_controller import LawyerController
from dtos.lawyer_models import LawyerModel as CreateLawyerRequest, UpdateLawyerRequest
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from config.db_config import get_db
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.auth_models import UserModel

lawyer=APIRouter(
    prefix='/lawyers',
    tags=['lawyers']
)

@lawyer.post("/lawyer", status_code=status.HTTP_201_CREATED)
async def create_lawyer(create_lawyer_request: CreateLawyerRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return LawyerController.create_lawyer(create_lawyer_request,user,db)

@lawyer.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return LawyerController.read_all(user,db)

@lawyer.patch("/lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def update_lawyer(lawyer_id: int,update_client_request: UpdateLawyerRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return LawyerController.update_lawyer(lawyer_id,update_client_request,user,db)
    
@lawyer.delete("/lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def delete_lawyer(lawyer_id: int, user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return LawyerController.delete_lawyer(lawyer_id,user,db)

@lawyer.put("/lawyer/{lawyer_id}/block", status_code=status.HTTP_200_OK)
async def block_lawyer(lawyer_id: int, user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return LawyerController.block_lawyer(lawyer_id,user,db)
    