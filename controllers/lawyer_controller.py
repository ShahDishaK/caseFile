# Importing libraries
from sqlalchemy import desc
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.users_table import User
from helper.api_helper import APIHelper
from sqlalchemy.orm import Session
from models.lawyers_table import Lawyers
from dtos.lawyer_models import LawyerModel as CreateLawyerRequest, UpdateLawyerRequest
from sqlalchemy.exc import SQLAlchemyError
from helper.hashing import Hash

class LawyerController:

    def create_lawyer(create_lawyer_request: CreateLawyerRequest, user: UserModel, db: Session):
        try:
            #  Step 1: Create new user
            user_model = User(
                name=create_lawyer_request.name,
                firstName=create_lawyer_request.firstName,
                lastName=create_lawyer_request.lastName,
                phoneNumber=create_lawyer_request.phoneNumber,
                address=create_lawyer_request.address,
                gender=create_lawyer_request.gender,
                email=create_lawyer_request.email,
                password=Hash.get_hash(create_lawyer_request.password),
                companyId=create_lawyer_request.companyId,
                role='lawyer'
            )

            db.add(user_model)
            db.commit()        
            db.refresh(user_model)  

            #  Step 2: Use generated user ID
            create_lawyer_model = Lawyers(
                userId=user_model.id,   
                specialization=create_lawyer_request.specialization,
            )

            db.add(create_lawyer_model)
            db.commit()

            return APIHelper.send_success_response(successMessageKey='translations.SUCCESS')

        except SQLAlchemyError as e:
            db.rollback()
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.DB_ERROR'
            )
    def read_all(user: UserModel ,db: Session ):
        lawyers = db.query(Lawyers, User).join(
                User, Lawyers.userId == User.id
            ).order_by(
                desc(Lawyers.createdAt) ).all()

        response_data= [
                {
                    "lawyer": lawyer,
                    "user": user
                }
                for lawyer, user in lawyers
            ]
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def update_lawyer(lawyer_id: int, update_lawyer_request: UpdateLawyerRequest, user: UserModel, db: Session):
        lawyer_model = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer_model,"LAWYER")

        # Update lawyer fields
        update_data = update_lawyer_request.dict(exclude_unset=True, exclude_none=True)

        for key, value in update_data.items():
            if hasattr(lawyer_model, key):
                setattr(lawyer_model, key, value)

        #  Update user fields
        user_model = db.query(User).filter(User.id == lawyer_model.userId).first()

        if user_model:
            if update_lawyer_request.name:
                user_model.name = update_lawyer_request.name
            if update_lawyer_request.phoneNumber:
                user_model.phoneNumber = update_lawyer_request.phoneNumber
            if update_lawyer_request.firstName:
                user_model.firstName = update_lawyer_request.firstName
            if update_lawyer_request.lastName:
                user_model.lastName = update_lawyer_request.lastName
            if update_lawyer_request.address:
                user_model.address = update_lawyer_request.address
            if update_lawyer_request.gender:
                user_model.gender = update_lawyer_request.gender
            # add more fields as needed
        db.commit()
        response_data= {
            "lawyer": lawyer_model,
            "user": user_model
            }
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )


    def delete_lawyer(lawyer_id: int, user: UserModel, db: Session):
            lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            lawyer.isDeleted = 1

            db.commit()
            db.refresh(lawyer)
            return APIHelper.send_success_response(successMessageKey='translations.SUCCESS')
   
    def block_lawyer(lawyer_id: int, user: UserModel,db: Session):
        db.query(Lawyers).filter(Lawyers.id == lawyer_id).update(
            {"isBlocked":b'\x01'}
        )

        db.commit()

        return APIHelper.send_success_response(successMessageKey='translations.SUCCESS')
    