from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import png_router, dicom_router, ai_dicom_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(png_router.router, prefix="/api")
app.include_router(dicom_router.router, prefix="/api")
app.include_router(ai_dicom_router.router, prefix="/api")

