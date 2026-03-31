# Importing libraries
from sqlalchemy import desc

from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from models.users_table import User
from models.staff_table import Staff
from models.clients_table import Clients
from models.lawyers_table import Lawyers
from helper.api_helper import APIHelper
from sqlalchemy.orm import Session
from dtos.client_models import ClientModel as CreateClientRequest, UpdateClientRequest
from helper.hashing import Hash
from models.cases_table import Cases
from models.documents_table import Documents
from models.tasks_table import Tasks
from models.caseStatusHistory_table import CaseStatusHistories
from models.courtSession_table import CourtSessions
from models.invoices_table import InvoiceStatus, Invoices


class ClientController:

    def create_client(create_client_request: CreateClientRequest, user: UserModel, db: Session):
        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        # block check
        ValidationHelper.block_check(lawyer.isBlocked)
        
        #  Step 2: Update user details
        try:
            user_model = User(
                    name=create_client_request.name,
                    firstName=create_client_request.firstName,
                    lastName=create_client_request.lastName,
                    phoneNumber=create_client_request.phoneNumber,
                    address=create_client_request.address,
                    gender=create_client_request.gender,
                    email=create_client_request.email,
                    password=Hash.get_hash(create_client_request.password),
                    companyId=create_client_request.companyId,
                    role='client'
                )

            db.add(user_model)
            db.commit()        
            db.refresh(user_model)  

            client = Clients(
                crNumber=create_client_request.crNumber,
                vatNumber=create_client_request.vatNumber,
                vatPercentage=create_client_request.vatPercentage,
                occupation=create_client_request.occupation,
                lawyerId=lawyer.id,
                userId=user_model.id,
            )

            db.add(client)
            db.commit()
            db.refresh(client)
            response_data={"client":client}
            return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )
        except:
            db.rollback()
            return APIHelper.send_bad_request_error(errorMessageKey="translations.DB_ERROR")

    def read_all(user: UserModel, db: Session):
        #  LAWYER
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # check blocked
            ValidationHelper.block_check(lawyer.isBlocked)

            clients = db.query(Clients, User).join(
                User, Clients.userId == User.id
            ).filter(
                Clients.lawyerId == lawyer.id,
                Clients.isDeleted == 0,
              
            ).order_by(
                desc(Clients.createdAt) ).all()

            response_data= [
                {
                    "client": client,
                    "user": user
                }
                for client, user in clients
            ]
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

        #  STAFF
        elif user.role=="staff":
            clients = db.query(Clients, User).join(
                User, Clients.userId == User.id
            ).join(
                Staff, Staff.lawyerId == Clients.lawyerId
            ).filter(
                Staff.user_id == user.id,
                Staff.isBlocked == 0,
                Clients.isDeleted == 0,
                
            ).order_by(
                desc(Clients.createdAt) ).all()

            # check lawyer exists
            ValidationHelper.check_role_exists(clients,"CLIENT")


            response_data= [
                {
                    "client": client,
                    "user": user
                }
                for client, user in clients
            ]
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )
        
        elif user.role=="admin":
            clients = db.query(Clients, User).join(
                User, Clients.userId == User.id
            ).all()
            response_data = [
                {
                    "client": client,
                    "user": user
                }
                for client, user in clients
            ]

            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )
    #  UPDATE CLIENT
    def update_client(client_id: int, update_client_request: UpdateClientRequest, user: UserModel, db: Session):
        client = db.query(Clients).filter(Clients.id == client_id, Clients.isDeleted == 0).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(client,"CLIENT")

        # check blocked
        ValidationHelper.block_check(client.isBlocked)
        #  LAWYER
        if user.role == 'lawyer':
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # block check
            ValidationHelper.block_check(lawyer.isBlocked)

            if client.lawyerId != lawyer.id:
                return APIHelper.send_forbidden_error(errorMessageKey='translations.NOT_ALLOWDED_TO_ACCESS_THIS_CLIENT')

        #  STAFF
        elif user.role=="staff":
            staff = db.query(Staff).filter(
                Staff.user_id == user.id,
                Staff.lawyerId == client.lawyerId,
                Staff.isBlocked == 0,
            ).first()
            # check lawyer exists
            ValidationHelper.check_role_exists(staff,"STAFF")
    
            # block check
            ValidationHelper.block_check(lawyer.isBlocked)


        # UPDATE LOGIC
        update_data = update_client_request.dict(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(client, key, value)
        #  Update user fields
        user_model = db.query(User).filter(User.id == client.userId).first()
        try:
            if user_model:
                if update_client_request.name:
                    user_model.name = update_client_request.name
                if update_client_request.phoneNumber:
                    user_model.phoneNumber = update_client_request.phoneNumber
                if update_client_request.firstName:
                    user_model.firstName = update_client_request.firstName
                if update_client_request.lastName:
                    user_model.lastName = update_client_request.lastName
                if update_client_request.address:
                    user_model.address = update_client_request.address
                if update_client_request.gender:
                    user_model.gender = update_client_request.gender
                # add more fields as needed

                db.commit()
                response_data= {
                    "lawyer": client,
                    "user": user_model
                    }
                return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )   
        except:
            return APIHelper.send_bad_request_error(errorMessageKey="translations.DB_ERROR")

    #  SOFT DELETE CLIENT
    def soft_delete_client(client_id: int, user: UserModel, db: Session):
        lawyer = db.query(Lawyers).filter(
            Lawyers.userId == user.id
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")
        # block check
        ValidationHelper.block_check(lawyer.isBlocked)


        client = db.query(Clients).filter(
            Clients.id == client_id,
            Clients.isDeleted == 0
        ).first()

        # check lawyer exists
        ValidationHelper.check_role_exists(client,"CLIENT")

        # chekck authorization
        ValidationHelper.check_authorization(client.lawyerId, lawyer.id, "CLIENT")

        try:
            # 1. Soft delete client
            pending_invoice = db.query(Invoices).filter(
                Invoices.clientId == client.id,
                Invoices.status == InvoiceStatus.pending,
                Invoices.isDeleted == 0
            ).first()

            if pending_invoice:
                return {"message": "Invoice of this client is pending"}
            client.isDeleted = 1

            # 2. Get all cases of this client
            cases = db.query(Cases).filter(
                Cases.clientId == client_id,
                Cases.isDeleted == 0
            ).all()

            case_ids = [case.id for case in cases]
            if case_ids:
                db.query(Cases).filter(Cases.id.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

                db.query(Invoices).filter(Invoices.caseId.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

                db.query(Documents).filter(Documents.caseId.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

                db.query(Tasks).filter(Tasks.caseId.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

                db.query(CaseStatusHistories).filter(CaseStatusHistories.caseId.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

                db.query(CourtSessions).filter(CourtSessions.caseId.in_(case_ids)).update({"isDeleted": 1}, synchronize_session=False)

            db.commit()

            response_data= {"message":"Client and all related data soft deleted successfully"}
            return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )


        except Exception as e:
            db.rollback()
            return APIHelper.send_bad_request_error(
                errorMessageKey='translations.DB_ERROR'
            )
    #  BLOCK CLIENT
    def block_client(client_id: int, user: UserModel, db: Session):
        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")
        # block check
        ValidationHelper.block_check(lawyer.isBlocked)

        client = db.query(Clients).filter(Clients.id == client_id).first()
        # check client exists
        ValidationHelper.check_role_exists(client,"CLIENT")
        # check authorization
        ValidationHelper.check_authorization(client.lawyerId, lawyer.id, "CLIENT")

        client.isBlocked = 1
        db.commit()
        response_data={"message":"Client blocked successfully"}
        return APIHelper.send_success_response(
                data=response_data,
                successMessageKey='translations.SUCCESS'
            )

