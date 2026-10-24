from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import pandas as pd

from schemas import AnalyzeRequest, AnalyzeResponse
from preprocess import preprocess
from scoring import ModelSettings, score, validate_settings
from money import expected_loss

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ML Service is ready")
    yield

app = FastAPI(title="ML Risk Analyzer", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        # 1. Инициализируем настройки и валидируем
        cfg = ModelSettings(**req.settings)
        validate_settings(cfg)

        # 2. Препроцессинг
        snap = preprocess(req.raw_data)

        # 3. Скоринг
        scored_df = score(snap, cfg)

        # 4. Расчет денежных потерь
        loss_df = expected_loss(snap, scored_df)

        # 5. Сборка сводки
        levels = scored_df["risk_level"].value_counts().reindex(["low", "medium", "high"], fill_value=0).to_dict()
        summary = {
            "customers_total": len(scored_df),
            "customers_by_level": {k: int(v) for k, v in levels.items()},
            "expected_loss_total_eur": round(float(loss_df["expected_loss_eur"].sum()), 2),
            "exposure_total_eur": round(float(loss_df["exposure_eur"].sum()), 2),
        }

        return {
            "summary": summary,
            "scored": scored_df.to_dict(orient="records"),
            "loss": loss_df.to_dict(orient="records")
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")