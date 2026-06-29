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


class DashboardStats(BaseModel):
    recommended_price: float
    revenue_impact: float
    occupancy_forecast: int
    active_alerts: int
    critical_alerts: int
    total_reservations: int
    monthly_revenue: float


class CompetitorPriceRow(BaseModel):
    ota: str
    yesterday: float
    today: float
    gap_pct: float
    trend: str


class TrendPoint(BaseModel):
    date: str
    price: float


class ReservationRow(BaseModel):
    id: str
    guest_name: str
    email: str
    check_in: str
    check_out: str
    nights: int
    guests: int
    room_type: str
    final_price: float
    status: str


class AlertRow(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    read: bool
    created_at: str
