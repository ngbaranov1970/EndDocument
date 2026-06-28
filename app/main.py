from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import document_router
from app.routers import archive_router
from app.routers import organization_router
from app.routers import user_router
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router.router)
app.include_router(archive_router.router)
app.include_router(organization_router.router)
app.include_router(user_router.router)