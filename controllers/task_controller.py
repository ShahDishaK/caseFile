# Importing libraries
from sqlalchemy import desc, func

from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from helper.api_helper import APIHelper
from models.staff_table import Staff
from models.lawyers_table import Lawyers
from models.tasks_table import Tasks, TaskStatus
from sqlalchemy.orm import Session
from dtos.task_models import TaskModel as CreateTaskRequest, UpdateTaskRequest
from datetime import date


class TaskController:

    def create_task(create_task_request: CreateTaskRequest, user: UserModel, db: Session):
        task = Tasks(
            title=create_task_request.title,
            description=create_task_request.description,
            caseId=create_task_request.caseId,
            assignedTo=user.id,
            dueDate=create_task_request.dueDate,
            priority=create_task_request.priority,
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        response_data= task
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def read_all(user: UserModel, db: Session):
        today = date.today()
        updated=False

        # Update status dynamically (not saving to DB)
        tasks = db.query(Tasks).filter(
            Tasks.assignedTo == user.id,
            Tasks.isDeleted == 0
        ).order_by(desc(Tasks.createdAt)).all()

        for task in tasks:
            if task.status == TaskStatus.PENDING and task.dueDate:
                if today > task.dueDate:
                    task.status = TaskStatus.OVERDUE
                    updated=True
        if updated:
            db.commit()

        # Counts (dynamic)
        pending_tasks = sum(1 for task in tasks if task.status == TaskStatus.PENDING)
        overdue_tasks = sum(1 for task in tasks if task.status == TaskStatus.OVERDUE)
        completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)

        response_data = {
            "tasks": tasks,
            "summary": {
                "pending": pending_tasks,
                "overdue": overdue_tasks,
                "completed": completed_tasks
            }
        }

        return APIHelper.send_success_response(
            data=response_data,
            successMessageKey='translations.SUCCESS'
        )

    def update_task(task_id: int, update_task_request: UpdateTaskRequest, user: UserModel, db: Session):
        task = db.query(Tasks).filter(
            Tasks.id == task_id,
            Tasks.isDeleted == 0
        ).first()

        # check task exists
        ValidationHelper.check_role_exists(task,"TASK")

        # chekck authorization
        ValidationHelper.check_authorization(task.assignedTo, user.id, "TASK")

        if task.status in [TaskStatus.COMPLETED, TaskStatus.OVERDUE]:
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.TASK_ALREADY_COMPLETED'
            )

        update_data = update_task_request.dict(exclude_unset=True, exclude_none=True)

        for key, value in update_data.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)

        response_data= task
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def delete_task(task_id: int, user: UserModel, db: Session):
        task = db.query(Tasks).filter(
            Tasks.id == task_id,
            Tasks.isDeleted == 0
        ).first()

        # check task exists
        ValidationHelper.check_role_exists(task,"TASK")

        # chekck authorization
        ValidationHelper.check_authorization(task.assignedTo, user.id, "TASK")

        # Delete allowed even if completed
        db.delete(task)
        db.commit()

        response_data= {"message": "Task deleted successfully"}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    def mark_as_done(task_id: int, user: UserModel, db: Session):
        task = db.query(Tasks).filter(
            Tasks.id == task_id,
            Tasks.isDeleted == 0
        ).first()

        # check task exists
        ValidationHelper.check_role_exists(task,"TASK")


        # chekck authorization
        ValidationHelper.check_authorization(task.assignedTo, user.id, "TASK")


        # Prevent re-marking
        if task.status in [TaskStatus.COMPLETED]:
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.TASK_ALREADY_COMPLETED'
            )

        # current_time = date.today()

        # if task.dueDate:
        #     if current_time <= task.dueDate:
        #         task.status = TaskStatus.COMPLETED
        #     else:
        #         task.status = TaskStatus.OVERDUE
        # else:
        task.status = TaskStatus.COMPLETED

        db.commit()
        db.refresh(task)

        response_data= task
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )