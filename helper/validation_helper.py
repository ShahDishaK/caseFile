from dtos.auth_models import UserModel
from helper.api_helper import APIHelper
from models.users_table import User
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ValidationHelper:
    def authenticate_user(username: str, password: str, db):
        user = db.query(User).filter(User.email == username).first()
        if user is None:
            return False
        if not bcrypt_context.verify(password, user.password):
            return False
        return user
    
    def check_user_exists(user: UserModel):
        if user is None :
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')

    def check_user_role(allowededRoles:list,user:UserModel):
        if user.role not in allowededRoles:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.FORBIDDEN')
    def block_check(blocked_value):
        if blocked_value==1:
            return APIHelper.send_forbidden_error(
                    errorMessageKey='translations.BLOCKED'
                )
    def check_role_exists(role,role_name:str):
        if not role:
                return APIHelper.send_not_found_error(
                    errorMessageKey=f'translations.{role_name}_NOT_FOUND'
                )
        
    def check_authorization(accessId, userId,action):
        if accessId != userId:
                return APIHelper.send_forbidden_error(
                    errorMessageKey=f'translations.NOT_ALLOWED_TO_ACCESS_THIS_{action}'
                )