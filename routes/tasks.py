# Importing libraries
from dtos.auth_models import UserModel
from fastapi import APIRouter, Depends
from fastapi import Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from fastapi import APIRouter,Depends
from starlette import status 
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.task_models import TaskModel as CreateTaskRequest, UpdateTaskRequest
from controllers.task_controller import TaskController

task=APIRouter(
    prefix='/tasks',
    tags=['tasks']
)


@task.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(create_task_request: CreateTaskRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return TaskController.create_task(create_task_request,user,db)

@task.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return TaskController.read_all(user,db)

@task.patch("/task/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    update_task_request: UpdateTaskRequest,
    user: UserModel = Depends(TokenHelper.get_current_user),
   db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return TaskController.update_task(task_id,update_task_request,user,db)

@task.delete("/task/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return TaskController.delete_task(task_id,user,db)

@task.patch("/task/{task_id}/markAsDone")
async def mark_task_done(
    task_id: int,
    user: UserModel = Depends(TokenHelper.get_current_user),
    db: Session = Depends(get_db)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","staff"],user) 
    return TaskController.mark_as_done(task_id, user, db)