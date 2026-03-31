from controllers.invoice_controller import InvoiceController
from dtos.invoice_models import InvoiceModel as CreateInvoiceRequest, UpdateInvoiceRequest
from fastapi import APIRouter, Depends , Request
from sqlalchemy.orm import Session
from starlette import status
from config.db_config import get_db
from helper.validation_helper import ValidationHelper
from helper.token_helper import TokenHelper
from dtos.auth_models import UserModel

invoice=APIRouter(
    prefix='/invoices',
    tags=['invoices']
)

@invoice.post("/invoice", status_code=status.HTTP_201_CREATED)
async def create_invoice(create_invoice_request: CreateInvoiceRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return InvoiceController.create_invoice(create_invoice_request,user,db)

@invoice.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer","client","admin"],user) 
    return InvoiceController.read_all(user,db)

@invoice.patch("/invoice/{invoice_id}", status_code=status.HTTP_200_OK)
async def update_invoice(invoice_id: int,update_invoice_request: UpdateInvoiceRequest,user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return InvoiceController.update_invoice(invoice_id,update_invoice_request,user,db)
    
@invoice.delete("/invoice/{invoice_id}", status_code=status.HTTP_200_OK)
async def delete_invoice(invoice_id: int, user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["lawyer"],user) 
    return InvoiceController.delete_invoice(invoice_id,user,db)

@invoice.get("/invoice/", status_code=status.HTTP_200_OK)
async def get_admin_invoice_totals(user: UserModel = Depends(TokenHelper.get_current_user),db: Session = Depends(get_db)):
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user) 
        return InvoiceController.get_admin_invoice_totals(user,db)
   
@invoice.post("/{invoice_id}/pay")
def create_payment_session(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(TokenHelper.get_current_user)
):
    ValidationHelper.check_user_exists(user)
    ValidationHelper.check_user_role(["client"],user) 
    return InvoiceController.create_payment_session(invoice_id, user, db)

@invoice.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    return await InvoiceController.handle_stripe_webhook(request, db)