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
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

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
        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id,
                Lawyers.isDeleted==0
            ).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

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

            # check if any histories are found
            ValidationHelper.check_role_exists(histories,"HISTORIES")

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
        # ================= LAWYER =================
        if user.role == 'lawyer':

            lawyer = db.query(Lawyers).filter(
                Lawyers.userId == user.id
            ).first()

            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            history = db.query(CaseStatusHistories).join(
                Cases, CaseStatusHistories.caseId == Cases.id
            ).filter(
                CaseStatusHistories.id == history_id,
                Cases.lawyerId == lawyer.id,
                CaseStatusHistories.isDeleted==0
            ).first()

            # check history exists
            ValidationHelper.check_role_exists(history,"HISTORY")
            

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

            # check history exists
            ValidationHelper.check_role_exists(history,"HISTORY")

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
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        history = db.query(CaseStatusHistories).filter(
            CaseStatusHistories.id == case_history_id,
                CaseStatusHistories.isDeleted==0
        ).first()

        # check history exists
        ValidationHelper.check_role_exists(history,"HISTORY")

        case = db.query(Cases).filter(
            Cases.id == history.caseId
        ).first()

        # check case exists
        ValidationHelper.check_role_exists(case,"CASE")

        # chekck authorization
        ValidationHelper.check_authorization(case.lawyerId, lawyer.id, "CASE")


        db.delete(history)
        db.commit()

        response_data= {"message": "Case history deleted successfully"}
        return APIHelper.send_success_response(
            data=response_data,
            successMessageKey='translations.SUCCESS'
        )