from pydantic import BaseModel, Field
from typing import Optional, Dict


class PredictRequest(BaseModel):
    property_type: str = Field("hotel", description="hotel | airbnb | hostel | rural")
    location: str = Field("", description="City or area")
    guests: int = Field(2, ge=1, le=20)
    nights: int = Field(1, ge=1, le=30)
    month: int = Field(7, ge=1, le=12)
    lead_time: int = Field(14, ge=0, le=365)
    room_type: str = Field("standard", description="standard | premium | suite")
    base_price: Optional[float] = Field(None, description="Current price if known")
    competitor_prices: Optional[Dict[str, float]] = Field(None, description="OTA prices")


class OTASavings(BaseModel):
    ota: str
    ota_price: float
    ota_net: float
    optimus_price: float
    savings_direct: float
    savings_pct: float


class PredictResponse(BaseModel):
    price: float
    currency: str = "EUR"
    features_used: int
    competitor_avg: Optional[float] = None
    savings_vs_ota: list[OTASavings] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool
    version: str = "2.0"
