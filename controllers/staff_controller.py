# Importing libraries
from sqlalchemy import desc

from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.users_table import User
from models.lawyers_table import Lawyers
from helper.api_helper import APIHelper
from models.staff_table import Staff
from models.blockedStaff_table import BlockedStaff
from sqlalchemy.orm import Session
from dtos.staff_models import StaffModel as CreateStaffRequest, UpdateStaffRequest
from helper.hashing import Hash

class StaffController:
    def create_staff(create_staff_request: CreateStaffRequest,user: UserModel,db: Session):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        #  Step 1: Get existing user
        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        #  Step 2: Update user details
        user_model = User(
                name=create_staff_request.name,
                firstName=create_staff_request.firstName,
                lastName=create_staff_request.lastName,
                phoneNumber=create_staff_request.phoneNumber,
                address=create_staff_request.address,
                gender=create_staff_request.gender,
                email=create_staff_request.email,
                password=Hash.get_hash(create_staff_request.password),
                companyId=create_staff_request.companyId,
                role='staff'
            )

        db.add(user_model)
        db.commit()        
        db.refresh(user_model)  

        create_staff_model = Staff(
            user_id=user_model.id,
            caseId=create_staff_request.caseId,
            lawyerId=lawyer.id,
        )
        db.add(create_staff_model)
        db.commit()
        response_data= create_staff_model
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def read_all(user: UserModel, db: Session):
        # check if user exists
        ValidationHelper.check_user_exists(user)
        # check if user is lawyer or admin
        ValidationHelper.check_user_role(["lawyer", "admin"], user)

        if user.role=="lawyer":
        # get lawyer using logged in user
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")
            # check blocked
            ValidationHelper.block_check(lawyer.isBlocked)

            staff=db.query(Staff,User).join(
                User,Staff.user_id==User.id
            ).join(Lawyers,Staff.lawyerId==Lawyers.id).filter(Staff.lawyerId == lawyer.id,
                ).order_by(
                desc(Staff.createdAt) ).all()
            return [
                {
                    "staff": staff,
                    "user": user
                }
                for staff, user in staff    
            ]
        elif user.role=="admin":
            staff=db.query(Staff,User).join(
                User,Staff.user_id==User.id
            ).join(Lawyers,Staff.lawyerId==Lawyers.id).all()
            return [
                {
                    "staff": staff,
                    "user": user
                }
                for staff, user in staff    
            ]
        

    def update_staff(
        staff_id: int,
        update_staff_request: UpdateStaffRequest,
        user: UserModel,
    db: Session
    ):
        staff_model = db.query(Staff).filter(Staff.id == staff_id).first()
        # check if user exists and is lawyer or admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer","admin"],user) 

        if staff_model is None:
            return APIHelper.send_not_found_error(errorMessageKey='translations.STAFF_NOT_FOUND')
        if user.role=="lawyer":
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")
            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            if staff_model.lawyerId==lawyer.id:
                update_data = update_staff_request.dict(exclude_unset=True, exclude_none=True)

                for key, value in update_data.items():
                    if hasattr(staff_model, key):
                        setattr(staff_model, key, value)
                
                #  Update user fields
                user_model = db.query(User).filter(User.id == Staff.user_id).first()
                try:
                    if user_model:
                        if update_staff_request.name:
                            user_model.name = update_staff_request.name
                        if update_staff_request.phoneNumber:
                            user_model.phoneNumber = update_staff_request.phoneNumber
                        if update_staff_request.firstName:
                            user_model.firstName = update_staff_request.firstName
                        if update_staff_request.lastName:
                            user_model.lastName = update_staff_request.lastName
                        if update_staff_request.address:
                            user_model.address = update_staff_request.address
                        if update_staff_request.gender:
                            user_model.gender = update_staff_request.gender
                    db.commit()
                    return {
                        "lawyer": staff_model,
                        "user": user_model
                        }
                except:
                    return APIHelper.send_bad_request_error(errorMessageKey="translations.DB_ERROR")
        elif user.role=="admin":
            update_data = update_staff_request.dict(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                if hasattr(staff_model, key):
                    setattr(staff_model, key, value)
                
                #  Update user fields
            user_model = db.query(User).filter(User.id == Staff.user_id).first()
            try:
                if user_model:
                    if update_staff_request.name:
                        user_model.name = update_staff_request.name
                    if update_staff_request.phoneNumber:
                        user_model.phoneNumber = update_staff_request.phoneNumber
                    if update_staff_request.firstName:
                        user_model.firstName = update_staff_request.firstName
                    if update_staff_request.lastName:
                        user_model.lastName = update_staff_request.lastName
                    if update_staff_request.address:
                        user_model.address = update_staff_request.address
                    if update_staff_request.gender:
                        user_model.gender = update_staff_request.gender
                db.commit()
                return {
                    "lawyer": staff_model,
                    "user": user_model
                    }
            except:
                return APIHelper.send_bad_request_error(errorMessageKey="translations.DB_ERROR")
       

    # delete the document
    def delete_staff(
        staff_id: int,
        user: UserModel ,
        db: Session
    ):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        staff_model = db.query(Staff).filter(Staff.id == staff_id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(staff_model,"STAFF")        
        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")
        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        if staff_model.lawyerId==lawyer.id:
            db.delete(staff_model)
            db.commit()
            return {"message": "Document deleted successfully"}
        else:
            return APIHelper.send_forbidden_error(
                errorMessageKey='translations.NOT_ALLOWED_TO_DELETE_THIS_STAFF'
            )

    # Block staff
    def block_staff(client_id: int, user: UserModel, db: Session):

        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        staff = db.query(Staff).filter(Staff.id == client_id).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(staff,"STAFF")

        # chekck authorization
        ValidationHelper.check_authorization(staff.lawyerId, lawyer.id, "STAFF")

        staff.isBlocked = 1

        db.commit()
        db.refresh(staff)

        blocked_entry = BlockedStaff(
            lawyerId=lawyer.id,
            staffId=client_id,
        )

        db.add(blocked_entry)
        db.commit()

        return {"message": "Client blocked successfully"}