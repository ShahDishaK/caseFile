from sqlalchemy import desc
from sqlalchemy.orm import Session
from helper.validation_helper import ValidationHelper
from helper.api_helper import APIHelper
from models.companies_table import Companies
from dtos.company_models import CompanyModel, UpdateCompanyRequest
from dtos.auth_models import UserModel
from sqlalchemy.exc import SQLAlchemyError


class CompanyController:

    def create_company(create_company_request: CompanyModel, user: UserModel, db: Session):
        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user) 

        company = Companies(
            name=create_company_request.name,
            Address=create_company_request.Address,
            phoneNumber=create_company_request.phoneNumber,
            email=create_company_request.email
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        response_data={"company":company}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )
   
    def read_all(user: UserModel, db: Session):
        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user) 

        company= db.query(Companies).order_by(
                desc(Companies.createdAt) ).all()
        response_data={"company":company}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )


    def update_company(company_id: int, update_company_request: UpdateCompanyRequest, user: UserModel, db: Session):

        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"], user)

        try:
            company = db.query(Companies).filter(Companies.id == company_id).first()

            # check COMPANY exists
            ValidationHelper.check_role_exists(company,"COMPANY")

            update_data = update_company_request.dict(exclude_unset=True, exclude_none=True)
            print(update_data)
            for key, value in update_data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            db.commit()
            db.refresh(company)

            return APIHelper.send_success_response(
                data={"company": company},
                successMessageKey='translations.SUCCESS'
            )

        except SQLAlchemyError as e:
            db.rollback()
            print("🔥 REAL ERROR:", str(e))   # 👈 VERY IMPORTANT
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.DB_ERROR'
            )
    def delete_company(company_id: int, user: UserModel, db: Session):

        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user)
        company = db.query(Companies).filter(Companies.id == company_id).first()

        if company is None:
            return APIHelper.send_not_found_error(errorMessageKey='translations.COMAPNY_NOT_FOUND')

        db.delete(company)
        db.commit()

        response_data= {"message": "Company deleted successfully"}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )