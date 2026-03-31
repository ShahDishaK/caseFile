from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from config.db_config import get_db
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.auth_models import UserModel
from dtos.company_models import CompanyModel, UpdateCompanyRequest
from controllers.company_controller import CompanyController

company = APIRouter(
    prefix="/companies",
    tags=["Company"]
)


@company.post("/company", status_code=status.HTTP_201_CREATED)
async def create_company(
    request: CompanyModel,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return CompanyController.create_company(request, user, db)


@company.get("/", status_code=status.HTTP_200_OK)
async def read_all(
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user) 
    return CompanyController.read_all(user, db)


@company.patch("/company/{company_id}", status_code=status.HTTP_200_OK)
async def update_company(
    company_id: int,
    request: UpdateCompanyRequest,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"], user)
    return CompanyController.update_company(company_id, request, user, db)

@company.delete("/company/{company_id}", status_code=status.HTTP_200_OK)
async def delete_company(
    company_id: int,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["admin"],user)
    return CompanyController.delete_company(company_id, user, db)