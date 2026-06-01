from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import document_router
from app.routers import organization_router
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

origins = [
    "http://localhost:5173",
    'http://127.0.1:5173',
     ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router.router)
app.include_router(organization_router.router)
