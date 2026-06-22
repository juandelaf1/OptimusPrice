from fastapi import APIRouter, HTTPException
from app.schemas.predict import PredictRequest, PredictResponse, HealthResponse
from app.services.ml_service import MLService

router = APIRouter()
ml = MLService()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(model_loaded=ml.model is not None)


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    try:
        data = req.model_dump()
        if not data.get("competitor_prices"):
            data["competitor_prices"] = {}
        result = ml.predict(data)
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
