from config.db_config import engine
from models.users_table import User 

class DBHelper:
    @staticmethod
    def get_user_by_email(email: str,db):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(id: int,db):
        return db.query(User).filter(User.id == id).first()