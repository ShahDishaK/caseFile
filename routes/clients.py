from controllers.client_controller import ClientController
from dtos.client_models import ClientModel as CreateClientRequest, UpdateClientRequest
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from config.db_config import get_db
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.auth_models import UserModel

client=APIRouter(
    prefix='/clients',
    tags=['clients']
)

@client.post("/client", status_code=status.HTTP_201_CREATED)
async def create_client(create_client_request: CreateClientRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return ClientController.create_client(create_client_request,user,db)

@client.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff","admin"],user) 
    return ClientController.read_all(user,db)

@client.patch("/client/{client_id}", status_code=status.HTTP_200_OK)
async def update_client(client_id: int,update_client_request: UpdateClientRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff","admin"],user) 
    return ClientController.update_client(client_id,update_client_request,user,db)
    
@client.delete("/client/{client_id}", status_code=status.HTTP_200_OK)
async def soft_delete_client(client_id: int, user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return ClientController.soft_delete_client(client_id,user,db)

@client.put("/client/{client_id}/block", status_code=status.HTTP_200_OK)
async def block_client(client_id: int, user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return ClientController.block_client(client_id,user,db)
