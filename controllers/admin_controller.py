# Importing libraries
from dtos.auth_models import UserModel
from helper.hashing import Hash
from models.companies_table import Companies
from models.users_table import User, UserRole
from helper.api_helper import APIHelper
from models.cases_table import Cases
from models.caseStatusHistory_table import CaseStatusHistories
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.cases_table import Cases, CaseStatus
from sqlalchemy import  func
from models.tasks_table import Tasks, TaskStatus
from dtos.admin_models import AdminModel as CreateAdminRequest
from models.users_table import User
from helper.validation_helper import ValidationHelper

class AdminController:
    # open cases, closed cases, and new cases in the last 30 days counts
    def get_case_counts(user: UserModel,db: Session):       
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        open_cases = db.query(func.count(Cases.id)).filter(
            Cases.status == CaseStatus.open,
            Cases.isDeleted == b'\x00'
        ).scalar()
        
        closed_cases = db.query(func.count(Cases.id)).filter(
            Cases.status == CaseStatus.closed,
            Cases.isDeleted == b'\x00'
        ).scalar()
        
        new_cases = db.query(func.count(Cases.id)).filter(
            Cases.createdAt >= thirty_days_ago,
            Cases.isDeleted ==b'\x00'
        ).scalar()

        response_data= {
            "openCases": open_cases,
            "closedCases": closed_cases,
            "newCasesLast30Days": new_cases
        }
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

    
    # case status count
    def get_case_status_count(user:UserModel,db:Session):
        last_thirty_days=datetime.utcnow()-timedelta(days=30)
        closed_last_30_days=db.query(func.count(CaseStatusHistories.id)).filter(
            CaseStatusHistories.updatedAt>=last_thirty_days,
        ).scalar()

        response_data= {
        "casesStatusChangeInLast30Days": closed_last_30_days
        }
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

    
    # task count based on due
    def task_counts(user:UserModel,db: Session):
        # check if user exists and is admin
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user)
        
        pending_tasks = db.query(func.count(Tasks.id)).filter(
            Tasks.status == TaskStatus.PENDING
        ).scalar()

        overdue_tasks = db.query(func.count(Tasks.id)).filter(
            Tasks.status == TaskStatus.OVERDUE
        ).scalar()

        completed_tasks = db.query(func.count(Tasks.id)).filter(
            Tasks.status == TaskStatus.COMPLETED
        ).scalar()

        response_data={
            "pending": pending_tasks,
            "overdue": overdue_tasks,
            "completed": completed_tasks
        }
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

    
    def company_users(company_id: int, user: UserModel, db: Session):
        company = db.query(Companies).filter(Companies.id == company_id).first()

        if company is None:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')

        lawyers = db.query(User).filter(
            User.companyId == company_id,
            User.role == UserRole.LAWYER,
        ).all()

        staff = db.query(User).filter(
            User.companyId == company_id,
            User.role == UserRole.STAFF,
        ).all()

        response_data= {
            "companyId": company.id,
            "companyName": company.name,
            "lawyers": lawyers,
            "staff": staff
        }
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

    def create_admins(create_admin_request: CreateAdminRequest,user: UserModel, db: Session):
        try:
            admin=User(
                name=create_admin_request.name,
                firstName=create_admin_request.firstName,
                lastName=create_admin_request.lastName,
                email=create_admin_request.email,
                password=Hash.get_hash(create_admin_request.password),
                phoneNumber=create_admin_request.phoneNumber,
                address=create_admin_request.address,
                gender=create_admin_request.gender,
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)  
            response_data={"admin":admin}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )
        except:
            db.rollback()
            return APIHelper.send_bad_request_error(errorMessageKey="translations.BD_ERROR")
