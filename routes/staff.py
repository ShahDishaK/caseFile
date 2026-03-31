# Importing libraries
from dtos.auth_models import UserModel
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from fastapi import APIRouter,Depends
from starlette import status 
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.staff_models import StaffModel as CreateStaffRequest, UpdateStaffRequest
from controllers.staff_controller import StaffController

staff=APIRouter(
    prefix='/staff',
    tags=['staff']
)


@staff.post("/staff", status_code=status.HTTP_201_CREATED)
async def create_staff(create_staff_request: CreateStaffRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return StaffController.create_staff(create_staff_request,user,db)

@staff.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer", "admin"], user)
    return StaffController.read_all(user,db)

@staff.patch("/staff/{staff_id}", status_code=status.HTTP_200_OK)
async def update_staff(
    staff_id: int,
    update_staff_request: UpdateStaffRequest,
    user: UserModel = Depends(TokenHelper.get_current_user),
   db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","admin"],user) 
    return StaffController.update_staff(staff_id,update_staff_request,user,db)

@staff.delete("/staff/{staff_id}", status_code=status.HTTP_200_OK)
async def delete_staff(
    staff_id: int,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return StaffController.delete_staff(staff_id,user,db)

@staff.put("/staff/{staff_id}/block", status_code=status.HTTP_200_OK)
async def block_staff(staff_id: int,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return StaffController.block_staff(staff_id,user,db)