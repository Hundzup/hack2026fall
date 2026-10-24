from pydantic import BaseModel
from typing import Any

class AnalyzeRequest(BaseModel):
    raw_data: dict
    settings: dict

class AnalyzeResponse(BaseModel):
    summary: dict
    scored: list[dict]
    loss: list[dict]