# Importing libraries
from dtos.auth_models import UserModel
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from typing_extensions import Annotated
from fastapi import APIRouter,Depends
from starlette import status 
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from controllers.document_controller import DocumentController
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

document=APIRouter(
    prefix='/documents',
    tags=['document']
)



user_dependency=Annotated[dict,Depends(TokenHelper.get_current_user)]


@document.post("/document", status_code=status.HTTP_201_CREATED)
async def create_document(
    title: str = Form(...),
    fileType: str = Form(...),
    description: str = Form(None),
    notes: str = Form(None),
    caseId: int = Form(...),
    clientId: int = Form(...),
    file: UploadFile = File(...),

    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return await DocumentController.create_document(
        title,
        fileType,
        description,
        notes,
        caseId,
        clientId,
        file,
        user,
        db
    )
@document.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer", "staff"], user)
    return DocumentController.read_all(user,db)

@document.patch("/document/{document_id}", status_code=status.HTTP_200_OK)
async def update_document(
    document_id: int,

    title: str = Form(None),
    fileType: str = Form(None),
    description: str = Form(None),
    notes: str = Form(None),
    caseId: int = Form(None),
    clientId: int = Form(None),

    file: UploadFile = File(None),

    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return await DocumentController.update_document(
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
    )
@document.delete("/document/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: int,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return DocumentController.delete_document(document_id,user,db)