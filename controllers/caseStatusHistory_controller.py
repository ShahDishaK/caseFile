from sqlalchemy import desc

from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.lawyers_table import Lawyers
from models.cases_table import Cases
from models.staff_table import Staff
from models.caseStatusHistory_table import CaseStatusHistories
from helper.api_helper import APIHelper
from sqlalchemy.orm import Session
from dtos.caseStatusHistory_models import CaseStatusHistoryModel as CreateCaseRequest, UpdateCaseStatusHistoryRequest

class CaseController:

    #  CREATE
    def create_case(create_case_request: CreateCaseRequest, user: UserModel, db: Session):

       # check if user exists and is lawyer
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 
      
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        if not lawyer:
            return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

        #  FIXED BLOCK CHECK
        if lawyer.isBlocked ==1:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED')
        try:
            new_history = CaseStatusHistories(
                caseId=create_case_request.caseId,
                oldStatus=create_case_request.oldStatus,
                newStatus=create_case_request.newStatus,
            )

            db.add(new_history)
            db.commit()
            db.refresh(new_history)

            response_data={"history":new_history}
            return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )
        except:
            db.rollback()
            return APIHelper.send_bad_request_error(errorMessageKey="translations.DB_ERROR")


    #  READ ALL
    def read_all(user: UserModel, db: Session):

        # check if user exists and is lawyer and staff
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer","staff"],user) 

        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id,
                Lawyers.isDeleted==0
            ).first()

            if not lawyer:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            histories = db.query(CaseStatusHistories).join(
                Cases, CaseStatusHistories.caseId == Cases.id
            ).filter(
                Cases.lawyerId == lawyer.id,
                CaseStatusHistories.isDeleted==0
            ).order_by(
                desc(CaseStatusHistories.createdAt) ).all()

            response_data={"sattus_histories":histories}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

        # ================= STAFF =================
        else:

            histories = db.query(CaseStatusHistories).join(
                Cases, CaseStatusHistories.caseId == Cases.id
            ).join(
                Staff, Staff.caseId == Cases.id
            ).filter(
                Staff.user_id == user.id,
                Staff.isBlocked == 0  ,
                CaseStatusHistories.isDeleted==0
            ).order_by(
                desc(CaseStatusHistories.createdAt) ).all()

            if not histories:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED_OR_NOT_ASSIGENED_TO_HISTORY')
            response_data={"sattus_histories":histories}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

    #  UPDATE
    def update_case(
        history_id: int,
        update_request: UpdateCaseStatusHistoryRequest,
        user: UserModel,
        db: Session
    ):

        # check if user exists and is lawyer and staff
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer","staff"],user) 

        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id
            ).first()

            if not lawyer:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')
            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            history = db.query(CaseStatusHistories).join(
                Cases, CaseStatusHistories.caseId == Cases.id
            ).filter(
                CaseStatusHistories.id == history_id,
                Cases.lawyerId == lawyer.id,
                CaseStatusHistories.isDeleted==0
            ).first()

            if not history:
                APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')


        # ================= STAFF =================
        else:

            history = db.query(CaseStatusHistories).join(
                Cases, CaseStatusHistories.caseId == Cases.id
            ).join(
                Staff, Staff.caseId == Cases.id
            ).filter(
                CaseStatusHistories.id == history_id,
                Staff.user_id == user.id,
                Staff.isBlocked ==0  ,
                CaseStatusHistories.isDeleted==0
            ).first()

            if not history:
                APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')


        #  UPDATE DATA
        update_data = update_request.dict(
            exclude_unset=True,
            exclude_none=True
        )

        for key, value in update_data.items():
            setattr(history, key, value)

        db.commit()
        db.refresh(history)

        response_data={"sattus_histories":history}
        return APIHelper.send_success_response(
            data=response_data,
            successMessageKey='translations.SUCCESS'
        )


    #  DELETE
    def delete_case(case_history_id: int, user: UserModel, db: Session):

        # check if user exists and is lawyer
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        if not lawyer:
            return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        history = db.query(CaseStatusHistories).filter(
            CaseStatusHistories.id == case_history_id,
                CaseStatusHistories.isDeleted==0
        ).first()

        if not history:
            return APIHelper.send_not_found_error(errorMessageKey='translations.HISTORY_NOT_FOUND')

        case = db.query(Cases).filter(
            Cases.id == history.caseId
        ).first()

        if not case:
            return APIHelper.send_not_found_error(errorMessageKey='translations.CASE_NOT_FOUND')

        if case.lawyerId != lawyer.id:
            APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')


        db.delete(history)
        db.commit()

        response_data= {"message": "Case history deleted successfully"}
        return APIHelper.send_success_response(
            data=response_data,
            successMessageKey='translations.SUCCESS'
        )