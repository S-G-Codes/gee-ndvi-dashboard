from fastapi import FastAPI
from app.api import ndvi

app = FastAPI(title="NDVI Dashboard API")

# Include routes
app.include_router(ndvi.router, prefix="/ndvi", tags=["NDVI"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
