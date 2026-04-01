# Loading the .env file
from dotenv import load_dotenv
from os.path import join, dirname
from helper.cors_helper import CORSHelper
from fastapi import FastAPI
from routes.users import router
from routes.cases import case
from routes.caseStatusHistory import caseStatus
from routes.clients import client
from routes.tasks import task
from routes.staff import staff
from routes.lawyers import lawyer
from routes.courtSessions import session
from routes.companies import company
from routes.documents import document
from routes.admin import admin
from routes.auth import auth
from routes.invoices import invoice
import os
import i18n

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
i18n.load_path.append(os.path.join(BASE_DIR, 'fastapi/language'))
i18n.set('filename_format', '{namespace}.{locale}.{format}')
i18n.set('fallback', 'en')
i18n.set('locale', 'en')


app = FastAPI()

# Base.metadata.create_all(bind=engine)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
CORSHelper.setup_cors(app)

app.include_router(router)
app.include_router(auth)
app.include_router(case)
app.include_router(caseStatus)
app.include_router(document)
app.include_router(client)
app.include_router(task)
app.include_router(staff)
app.include_router(session)
app.include_router(company)
app.include_router(lawyer)
app.include_router(admin)
app.include_router(invoice)












