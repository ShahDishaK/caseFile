# Importing libraries
from sqlalchemy import desc

from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.cases_table import Cases
from helper.api_helper import APIHelper
from models.lawyers_table import Lawyers
from models.courtSession_table import CourtSessions
from sqlalchemy.orm import Session
from fastapi import HTTPException
from dtos.courtsession_models import SessionModel as CreatSessionRequest

class CourtSessionController:

    def create_document(create_session_request: CreatSessionRequest,user: UserModel,db: Session ):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        
        create_session_model = CourtSessions(
            sessionDate=create_session_request.sessionDate,
            sessionTime=create_session_request.sessionTime,
            courtName=create_session_request.courtName,
            caseId=create_session_request.caseId,
            lawyerId=lawyer.id,
            clientId=create_session_request.clientId,
        )
        db.add(create_session_model)
        db.commit()
        response_data={"session":create_session_model}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def read_all(user: UserModel, db: Session):
# check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")


        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        sessions = db.query(CourtSessions, Cases).join(
            Cases, CourtSessions.caseId == Cases.id
        ).filter(
            CourtSessions.lawyerId == lawyer.id,
            Cases.isDeleted == 0
        ).order_by(
                desc(CourtSessions.createdAt) ).all()
        response_data= [
            {
                "session": session,
                "case": case
            }
            for session, case in sessions
        ]
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )