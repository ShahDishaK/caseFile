# Importing libraries
from dtos.auth_models import UserModel
from helper.api_helper import APIHelper
from models.staff_table import Staff
from models.lawyers_table import Lawyers
from models.documents_table import Documents
from models.cases_table import Cases
from sqlalchemy.orm import Session
from fastapi import HTTPException
import base64
import requests
from fastapi import UploadFile, File
import base64
from fastapi import HTTPException

class DocumentController:

    async def create_document(
        title,
        fileType,
        description,
        notes,
        caseId,
        clientId,
        file,
        user,
        db
    ):

        if user is None :
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        if user.role not in ['lawyer','staff']:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.FORBIDDEN')

        #  LAWYER CHECK
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            if lawyer is None:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

            if lawyer.isBlocked ==0:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED')

        #  STAFF CHECK
        else:
            staff = db.query(Staff).filter(
                Staff.user_id == user.id,
                Staff.caseId == caseId,
                Staff.isBlocked == 0
            ).first()

            if staff is None:
                return APIHelper.send_forbidden_error(
                    errorMessageKey='translations.BLOCKED_OR_NOT_ASSIGNED'
                )

        #  FILE → BASE64
        try:
            file_content = await file.read()
            base64_content = base64.b64encode(file_content).decode("utf-8")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error converting file: {str(e)}")

        # SAVE
        document = Documents(
            title=title,
            documentLink=base64_content,
            fileType=fileType,
            description=description,
            notes=notes,
            caseId=caseId,
            userId=user.id,
            clientId=clientId
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document


    #  READ ALL DOCUMENTS
    def read_all(user: UserModel, db: Session):

        if user is None:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        if user.role not in ['lawyer','staff']:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.FORBIDDEN')

        #  LAWYER
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            if lawyer is None:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

            if lawyer.isBlocked == 1 or lawyer.isDeleted==1:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED_OR_DELETED')

            documents = db.query(Documents, Cases).join(
                    Cases, Documents.caseId == Cases.id
                ).filter(
                    Cases.lawyerId == lawyer.id,
                    Documents.isDeleted == 0,
                    Cases.isDeleted == 0
                ).all()

            return [
                    {
                        "document":doc,
                        "case":case
                    }
                    for doc, case in documents
                ]

        #  STAFF
        else:
            documents = db.query(Documents).join(
                Cases, Documents.caseId == Cases.id
            ).join(
                Staff, Staff.caseId == Cases.id
            ).filter(
                Staff.user_id == user.id,
                Staff.isBlocked == 0,
                Documents.isDeleted==0
            ).all()

            if not documents:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED_OR_NOT_AVAILABLE_DOCUMENTS')
                

            return documents


    #  UPDATE DOCUMENT
    async def update_document(
    document_id,
    title,
    fileType,
    description,
    notes,
    caseId,
    clientId,
    file,
    user,
    db
):

        if user is None:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        if user.role not in ['lawyer','staff']:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.FORBIDDEN')

        document = db.query(Documents).filter(Documents.id == document_id,Documents.isDeleted==0).first()

        if document is None:
            return APIHelper.send_not_found_error(errorMessageKey='translations.DOCUMENT_NOT_FOUND')

        # LAWYER CHECK
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            if lawyer is None:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

            if lawyer.isBlocked == 1:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED')

        #  STAFF CHECK
        else:
            staff = db.query(Staff).filter(
                Staff.user_id == user.id,
                Staff.caseId == document.caseId,
                Staff.isBlocked == 0,
            ).first()

            if staff is None:
                return APIHelper.send_forbidden_error(
                    errorMessageKey='translations.BLOCKED_OR_NOT_ASSIGNED_TO_DOCUMENT'
                )

        #  FILE UPDATE (ONLY IF PROVIDED)
        if file:
            try:
                file_content = await file.read()
                document.documentLink = base64.b64encode(file_content).decode("utf-8")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error converting file: {str(e)}")

        # FIELD UPDATES (ONLY IF PROVIDED)
        if title is not None:
            document.title = title

        if fileType is not None:
            document.fileType = fileType

        if description is not None:
            document.description = description

        if notes is not None:
            document.notes = notes

        if caseId is not None:
            document.caseId = caseId

        if clientId is not None:
            document.clientId = clientId

        db.commit()
        db.refresh(document)

        return document


    #  DELETE DOCUMENT
    def delete_document(document_id: int, user: UserModel, db: Session):

        if user is None:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        if user.role not in ['lawyer','staff']:
            return APIHelper.send_forbidden_error(errorMessageKey='translations.FORBIDDEN')

        document = db.query(Documents).filter(Documents.id == document_id,Documents.isDeleted==0).first()

        if document is None:
            return APIHelper.send_not_found_error(errorMessageKey='translations.DOCUMENT_NOT_FOUND')

        #  LAWYER
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()

            if lawyer is None:
                return APIHelper.send_not_found_error(errorMessageKey='translations.LAWYER_NOT_FOUND')

            if lawyer.isBlocked == 1:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED')

            case = db.query(Cases).filter(Cases.id == document.caseId).first()

            if case.lawyerId != lawyer.id:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.NO_ACCESS_TO_THIS_DOCUMENT')

        #  STAFF
        else:
            staff = db.query(Staff).filter(
                Staff.user_id == user.id,
                Staff.caseId == document.caseId,
                Staff.isBlocked == 0
            ).first()

            if staff is None:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.BLOCKED_OR_NOT_ASSIGNED_TO_CASE')
                

        db.delete(document)
        db.commit()

        return {"message": "Document deleted successfully"}