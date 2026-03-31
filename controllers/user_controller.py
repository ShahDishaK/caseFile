# Importing libraries
from sqlalchemy import desc
from sqlalchemy.orm import Session
from dtos.user_models import UpdateUserProfile, UserVerification,ForgotPassword
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from helper.api_helper import APIHelper
from models.users_table import User
from fastapi import HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()
SECREAT_KEY=os.getenv("SECREAT_KEY")
ALGORITHM='HS256'

bcrypt_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='/auth/login')

class UserController:
    def read_all(user: UserModel ,db: Session ):
        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user) 
        users = db.query(User).order_by(
                desc(User.createdAt) ).all()
        response_data= users
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )


    def get_user(user: UserModel,db: Session):
        # check if user exists
        ValidationHelper.check_user_exists(user)
        user = db.query(User).filter(User.id == user.id).first()
        response_data= user
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def change_password(user_verification: UserVerification,user: UserModel,db: Session ):
        # check if user exists
        ValidationHelper.check_user_exists(user)
        user_model = db.query(User).filter(User.id == user.id).first()

        if not bcrypt_context.verify(user_verification.password, user_model.password):
            raise HTTPException(status_code=401, detail='Error on password change')
        user_model.password = bcrypt_context.hash(user_verification.new_password)
        db.add(user_model)
        db.commit()
        return APIHelper.send_success_response(
                    successMessageKey='translations.PASSWORD_CHANGED_SUCCESSFULL'
                )

    def forgot_password(user_verification: ForgotPassword, db: Session):
        
        user_model = db.query(User).filter(User.email == user_verification.email).first()

        # Check if the email matches
        # check user exists
        ValidationHelper.check_role_exists(user_model,"USER")
        # Update password
        user_model.password = bcrypt_context.hash(user_verification.new_password)
        db.add(user_model)
        db.commit()

        response_data= {"message": "Password changed successfully"}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.PASSWORD_CHANGED_SUCCESSFULL'
                )

    def update_profile(update_user_profile: UpdateUserProfile, user: UserModel, db: Session):
        # check if user exists
        ValidationHelper.check_user_exists(user)
        user_model = db.query(User).filter(User.id == user.id).first()

        update_data = update_user_profile.dict(exclude_unset=True, exclude_none=True)

        for key, value in update_data.items():
            setattr(user_model, key, value)
                
        db.commit()
        db.refresh(user_model)

        response_data= user_model
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

