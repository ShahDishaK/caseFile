from dtos.auth_models import UserModel
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from fastapi import APIRouter,Depends
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from controllers.admin_controller import AdminController
from dtos.admin_models import AdminModel as CreateAdminRequest
from models.users_table import UserRole

admin=APIRouter(
    prefix='/admins',
    tags=['dashboard']
)

@admin.get("/dashboard/case_counts")
async def case_counts(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user)
    return AdminController.get_case_counts(user,db)

@admin.get("/dashboard/status_counts")
async def get_case_status_count(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user)
    return AdminController.get_case_status_count(user,db)

@admin.get("/dashboard/task_counts")
async def task_counts(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user)
    return AdminController.task_counts(user,db)

@admin.get("/dashboard/employees/{company_id}")
async def comapny_users(company_id:int,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user)
    return AdminController.company_users(company_id,user,db)

@admin.post("/dashboard/")
async def create_admins(create_admin_request:CreateAdminRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role([UserRole.ADMIN],user)
    return AdminController.create_admins(create_admin_request,user,db)
