from contextlib import asynccontextmanager
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = "model.pkl"
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    _model = joblib.load(MODEL_PATH)
    print(f"model loaded from {MODEL_PATH}")
    yield
    _model = None


app = FastAPI(title="ML Service", lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_length=1)


class PredictResponse(BaseModel):
    prediction: float
    model: str = "linear_regression"


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    expected = _model.n_features_in_
    if len(req.features) != expected:
        raise HTTPException(
            status_code=400,
            detail=f"expected {expected} features, got {len(req.features)}",
        )

    X = np.array(req.features, dtype=float).reshape(1, -1)
    y = float(_model.predict(X)[0])
    return PredictResponse(prediction=y)