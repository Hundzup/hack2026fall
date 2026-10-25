from pydantic import BaseModel
from typing import Any

class AnalyzeRequest(BaseModel):
    raw_data: dict
    settings: dict

class AnalyzeResponse(BaseModel):
    summary: dict
    scored: list[dict]
    loss: list[dict]
    
class ReasonItem(BaseModel):
    feature: str
    contribution: float
    title: str

class UserRiskMetrics(BaseModel):
    customer_id: int
    email: str
    balance_eur: float
    total_replenished_eur: float
    risk_score: float
    risk_level: str
    reasons: list[ReasonItem]

class UsersRiskResponse(BaseModel):
    users: list[UserRiskMetrics]
    
class UpdateSettingsRequest(BaseModel):
    settings: dict