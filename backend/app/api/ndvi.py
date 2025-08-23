from fastapi import APIRouter

router = APIRouter()

@router.get("/tile")
def get_tile():
    return {"message": "Tile URL will be here"}

@router.post("/stats")
def get_stats():
    return {"message": "NDVI stats will be here"}

@router.post("/timeseries")
def get_timeseries():
    return {"message": "Time-series data will be here"}
