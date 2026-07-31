from fastapi import FastAPI

from app.routers.client import router as client_router
from app.routers.reparation import router as reparation_router
from app.routers.utilisateur import router as utilisateur_router
from app.routers.facture_scan import router as facture_scan_router
from app.routers import ocr
from app.routers import stock
from app.routers import alerte_stock
from app.routers import client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.ocr import router as ocr_router

app = FastAPI(
    title="Repair Platform API"
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.include_router(client_router)
app.include_router(reparation_router)
app.include_router(utilisateur_router)
app.include_router(facture_scan_router)

@app.get("/")
def root():
    return {
        "message": "API Repair Platform"
    }

app.include_router(
    ocr.router
)

app.include_router(

    stock.router
)

app.include_router(

    alerte_stock.router

)

app.include_router(
    client.router
)

app.include_router(
    ocr_router
)