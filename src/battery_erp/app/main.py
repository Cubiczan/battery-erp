from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from battery_erp.app.api import black_mass, chemicals, lab, process, recipes
from battery_erp.app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Green Li-ion Hydrometallurgical Battery Recycling ERP",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(black_mass.router, prefix="/api/v1/black-mass", tags=["Black Mass"])
app.include_router(chemicals.router, prefix="/api/v1/chemicals", tags=["Chemicals"])
app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["Recipes"])
app.include_router(process.router, prefix="/api/v1/batches", tags=["Process Batches"])
app.include_router(lab.router, prefix="/api/v1/lab", tags=["Lab & NMC"])


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "version": "2.0.0"}
