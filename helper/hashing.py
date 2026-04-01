from passlib.context import CryptContext
from helper.api_helper import APIHelper
from dtos.auth_models import UserModel
from utils.db_helper import DBHelper

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def get_hash(text: str):
        return bcrypt_context.hash(text)

    def verify(plain_text: str, hashed_text: str):
        return bcrypt_context.verify(plain_text, hashed_text)

    def authenticate_user(username: str, password: str) -> UserModel:
        user = DBHelper.get_user_by_email(username)
        if not user and not Hash.verify(password, user.password):
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.INVALID_CREDENTIAL')
        return UserModel(**user._mapping)
