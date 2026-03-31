# Importing libraries
from sqlalchemy import desc
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.documents_table import Documents
from models.tasks_table import Tasks
from models.invoices_table import Invoices
from models.staff_table import Staff
from models.lawyers_table import Lawyers
from models.cases_table import Cases
from models.caseStatusHistory_table import CaseStatusHistories
from helper.api_helper import APIHelper
from sqlalchemy.orm import Session
from dtos.case_models import CaseModel as CreateCaseRequest, UpdateCaseRequest
from sqlalchemy.exc import SQLAlchemyError

class CaseController:

    #  CREATE CASE
    def create_case(create_case_request:CreateCaseRequest, user: UserModel, db: Session):
               
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        try:
            case = Cases(
                caseNumber=create_case_request.caseNumber,
                title=create_case_request.title,
                type=create_case_request.type,
                description=create_case_request.description,
                lawyerId=lawyer.id,
                caseStage=create_case_request.caseStage,
                caseCity=create_case_request.caseCity,
                status=create_case_request.status,
                caseClosedDate=create_case_request.caseClosedDate,
                clientId=create_case_request.clientId,
                isDeleted=0
            )

            db.add(case)
            db.commit()
            db.refresh(case)

            response_data={"case":case}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )
        except SQLAlchemyError as e:
            db.rollback() 
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.DB_ERROR'
            )


    #  READ ALL CASES
    def read_all(user: UserModel, db: Session):
        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id,
                Lawyers.isDeleted == 0,
            ).first()
            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            cases = db.query(Cases).filter(
                Cases.lawyerId == lawyer.id,
                Cases.isDeleted ==0
            ).order_by(
                desc(Cases.createdAt) ).all()

            response_data={"cases":cases}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

        # ================= STAFF =================
        elif user.role == 'staff':

            staff_records = db.query(Staff).filter(
                Staff.user_id == user.id
            ).all()

            # check staff exists
            ValidationHelper.check_role_exists(staff_records,"STAFF")

            allowed_case_ids = [
                staff.caseId
                for staff in staff_records
                if staff.isBlocked == 0 and staff.caseId is not None
            ]

            if not allowed_case_ids:
                return APIHelper.send_forbidden_error(
                    errorMessageKey='translations.BLOCKED'
                )

            cases = db.query(Cases).filter(
                Cases.id.in_(allowed_case_ids),
                Cases.isDeleted == 0
            ).order_by(
                desc(Cases.createdAt) ).all()

            response_data={"cases":cases}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )


    #  UPDATE CASE
    def update_case(case_id: int, update_case_request:UpdateCaseRequest, user: UserModel, db: Session):
        case = db.query(Cases).filter(
            Cases.id == case_id,
            Cases.isDeleted == 0
        ).first()

        # check case exists
        ValidationHelper.check_role_exists(case,"CASE")

        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id,
                Lawyers.isDeleted == 0
            ).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            # chekck authorization
            ValidationHelper.check_authorization(case.lawyerId, lawyer.id, "CASE")

        # ================= STAFF =================
        elif user.role == 'staff':

            allowed = db.query(Cases).join(
                Staff, Cases.id == Staff.caseId
            ).filter(
                Cases.id == case_id,
                Staff.user_id == user.id,
                Staff.isBlocked == 0
            ).first()

            if not allowed:
                return APIHelper.send_unauthorized_error(
                    errorMessageKey='translations.UNAUTHORIZED'
                )

        #  UPDATE DATA
        old_status = case.status

        update_data = update_case_request.dict(
            exclude_unset=True,
            exclude_none=True
        )

        for key, value in update_data.items():
            setattr(case, key, value)

        new_status = case.status

        if "status" in update_data and old_status != new_status:
            history = CaseStatusHistories(
                caseId=case.id,
                oldStatus=old_status,
                newStatus=new_status,
                                        )
            db.add(history)

        db.commit()
        db.refresh(case)

        response_data={"case":case}
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )


    #  SOFT DELETE
    def soft_delete_case(case_id: int, user: UserModel, db: Session):
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")


        # block check
        ValidationHelper.block_check(lawyer.isBlocked)


        case = db.query(Cases).filter(
            Cases.id == case_id,
            Cases.isDeleted == 0
        ).first()

        # check case exists
        ValidationHelper.check_role_exists(case,"CASE")

        # chekck authorization
        ValidationHelper.check_authorization(case.lawyerId, lawyer.id, "CASE")


        try:
            # Soft delete case
            case.isDeleted = b'\x01'

            # Soft delete related data

            db.query(Documents).filter(
                Documents.caseId == case_id
            ).update({"isDeleted": b'\x01'})

            db.query(Tasks).filter(
                Tasks.caseId == case_id
            ).update({"isDeleted": b'\x01'})

            db.query(CaseStatusHistories).filter(
                CaseStatusHistories.caseId == case_id
            ).update({"isDeleted": b'\x01'})

            db.query(Invoices).filter(
                Invoices.caseId == case_id,Invoices.status != 'paid'
            ).update({"isDeleted": b'\x01'})
            db.commit()

            response_data= {"message": "Case and related data soft deleted successfully"}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )
        except Exception as e:
            db.rollback()
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.DB_ERROR'
            )