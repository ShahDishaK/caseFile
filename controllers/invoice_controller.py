from helper.validation_helper import ValidationHelper
from models.clients_table import Clients
import stripe
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, Request
from dtos.invoice_models import InvoiceModel, UpdateInvoiceRequest
from models.invoices_table import Invoices, InvoiceStatus
from models.users_table import User, UserRole
from models.lawyers_table import Lawyers
from helper.api_helper import APIHelper
import os
from dotenv import load_dotenv
import json

load_dotenv()
key=os.getenv("STRIPE_API_KEY")
stripe.api_key = key


class InvoiceController:

    # ================= LAWYER CREATES INVOICE =================
    def create_invoice(create_invoice_request: InvoiceModel, user: User, db: Session):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")

        # check blocked
        ValidationHelper.block_check(lawyer.isBlocked)
        
        invoice = Invoices(
            totalAmount=create_invoice_request.totalAmount,
            totalHours=create_invoice_request.totalHours,
            caseId=create_invoice_request.caseId,
            clientId=create_invoice_request.clientId,
            lawyerId=lawyer.id,
            status=InvoiceStatus.pending,
            companyId=create_invoice_request.companyId,
            paymentStatus="pending"
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        response_data={"invoice":invoice}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    # ================= CREATE STRIPE PAYMENT SESSION =================
    def create_payment_session(invoice_id: int, user: User, db: Session):
        # check if user exists and is client 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["client"],user) 

        invoice = db.query(Invoices).filter(
            Invoices.id == invoice_id,
            Invoices.clientId == Clients.id
        ).first()
        if invoice.status==InvoiceStatus.paid:
            return APIHelper.send_bad_request_error(
                    errorMessageKey="translations.INVOICE_ALREADY_PAID"
                        )
        # check lawyer exists
        ValidationHelper.check_role_exists(invoice,"INVOICE")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Invoice #{invoice.id}",
                        },
                        "unit_amount": int(invoice.totalAmount * 100),  # convert to cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:5173/invoice",
                cancel_url="http://localhost:5173/invoice",
                metadata={
                    "invoice_id": str(invoice.id)
                }
            )

            # Save Stripe session ID
            invoice.stripeSessionId = session.id
            db.commit()

            return {"checkout_url": session.url}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ================= STRIPE WEBHOOK =================
    async def handle_stripe_webhook(request: Request, db: Session):
        payload = None
        try:
            payload = await request.body()
            sig_header = request.headers.get("stripe-signature")

            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                os.getenv("STRIPE_WEBHOOK_SECRET"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")

        #  PAYMENT SUCCESS
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            invoice_id = session["metadata"]["invoice_id"]

            invoice = db.query(Invoices).filter(Invoices.id == int(invoice_id)).first()

            if invoice:
                invoice.status = "paid"
                invoice.paymentStatus = "success"
                invoice.stripePaymentIntentId = session.get("payment_intent")
                invoice.paymentMethod = "card"
                invoice.paidAt = datetime.utcnow()

                db.commit()

        #  PAYMENT FAILED (optional handling)
        if event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]

            invoice = db.query(Invoices).filter(
                Invoices.stripePaymentIntentId == intent["id"]
            ).first()

            if invoice:
                invoice.paymentStatus = "failed"
                db.commit()

        return {"status": "success"}

    # ================= READ INVOICES =================
    def read_all(user: User, db: Session, status: str = None):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer","client","admin"],user) 

        if user.role == UserRole.LAWYER:
            lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
            # check lawyer exists
            ValidationHelper.check_role_exists(lawyer,"LAWYER")

            # check blocked
            ValidationHelper.block_check(lawyer.isBlocked)
            query = db.query(Invoices).filter(Invoices.lawyerId == lawyer.id,Invoices.isDeleted==0)

        elif user.role == UserRole.CLIENT:
            client = db.query(Clients).filter(Clients.userId == user.id).first()
            query = db.query(Invoices).filter(Invoices.clientId == client.id,Invoices.isDeleted==0)

        else:
            query = db.query(Invoices)

        if status:
            try:
                status_enum = InvoiceStatus(status)
                query = query.filter(Invoices.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")

        response_data=query.order_by(
                desc(Invoices.createdAt) ).all()
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    # ================= UPDATE INVOICE =================
    def update_invoice(invoice_id: int, update_invoice_request: UpdateInvoiceRequest, user: User, db: Session):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")
        # check blocked
        ValidationHelper.block_check(lawyer.isBlocked)

        invoice = db.query(Invoices).filter(Invoices.id == invoice_id,Invoices.isDeleted==0).first()
        if not invoice:
            return APIHelper.send_not_found_error('translations.INVOICE_NOT_FOUND')

        # chekck authorization
        ValidationHelper.check_authorization(invoice.lawyerId, lawyer.id, "INVOICE")

        if invoice.status==InvoiceStatus.paid:
            return APIHelper.send_bad_request_error(
                    errorMessageKey="translations.INVOICE_ALREADY_PAID"
                        )
        update_data = update_invoice_request.dict(exclude_unset=True, exclude_none=True)

        for key, value in update_data.items():
            if key == "status":
                setattr(invoice, key, InvoiceStatus(value))
            else:
                setattr(invoice, key, value)

        db.commit()
        db.refresh(invoice)

        return invoice

    # ================= DELETE INVOICE =================
    def delete_invoice(invoice_id: int, user: User, db: Session):
        # check if user exists and is lawyer 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["lawyer"],user) 

        lawyer = db.query(Lawyers).filter(Lawyers.userId == user.id).first()
        # check lawyer exists
        ValidationHelper.check_role_exists(lawyer,"LAWYER")
        # check blocked
        ValidationHelper.block_check(lawyer.isBlocked)

        invoice = db.query(Invoices).filter(Invoices.id == invoice_id,Invoices.isDeleted==0).first()
        if not invoice:
            return APIHelper.send_not_found_error('translations.INVOICE_NOT_FOUND')

        # chekck authorization
        ValidationHelper.check_authorization(invoice.lawyerId, lawyer.id, "INVOICE")

        if invoice.status==InvoiceStatus.paid:
            return APIHelper.send_bad_request_error(
                    errorMessageKey="translations.INVOICE_ALREADY_PAID"
                        )
        db.delete(invoice)
        db.commit()

        response_data= {"message": "Invoice deleted successfully"}
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )

    # ================= ADMIN TOTALS =================
    def get_admin_invoice_totals(user: User, db: Session):
        # check if user exists and is admin 
        ValidationHelper.check_user_exists(user)
        ValidationHelper.check_user_role(["admin"],user) 

        total_paid = db.query(func.sum(Invoices.totalAmount)) \
            .filter(Invoices.status == InvoiceStatus.paid).scalar() or 0

        total_pending = db.query(func.sum(Invoices.totalAmount)) \
            .filter(Invoices.status == InvoiceStatus.pending).scalar() or 0

        invoices = db.query(Invoices).filter(Invoices.isDeleted==0).all()

        response_data= {
            "invoices": invoices,
            "total_paid": float(total_paid),
            "total_pending": float(total_pending)
        }
        return APIHelper.send_success_response(
                    data=response_data,
                    successMessageKey='translations.SUCCESS'
                )