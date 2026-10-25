from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
import pandas as pd

from schemas import AnalyzeRequest, AnalyzeResponse, UsersRiskResponse, UserRiskMetrics
from schemas import UpdateSettingsRequest
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
        
        cfg = ModelSettings(**req.settings)
        validate_settings(cfg)

        
        snap = preprocess(req.raw_data)

        
        scored_df = score(snap, cfg)


        loss_df = expected_loss(snap, scored_df)


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
    
    
@app.post("/users-risks", response_model=UsersRiskResponse, tags=["Analytics"])
def get_users_risks(req: AnalyzeRequest):
    """
    Возвращает полный список клиентов с их оценкой риска и причинами.
    Идеально для отрисовки главной таблицы на фронтенде.
    """
    try:
        
        cfg = ModelSettings(**req.settings)
        validate_settings(cfg)

        
        snap = preprocess(req.raw_data)

        
        scored_df = score(snap, cfg)

        
        acc_info = snap.accounts[["id", "email", "balance_eur", "totalReplenished_eur"]]
        
        
        full_df = scored_df.merge(
            acc_info, 
            left_on="customer_id", 
            right_on="id", 
            how="left"
        )

        
        users_list = []
        for _, row in full_df.iterrows():
            users_list.append(UserRiskMetrics(
                customer_id=int(row["customer_id"]),
                email=str(row["email"]),
                balance_eur=round(float(row["balance_eur"]), 2),
                total_replenished_eur=round(float(row["totalReplenished_eur"]), 2),
                risk_score=float(row["risk_score"]),
                risk_level=str(row["risk_level"]),
                reasons=row["reasons"] 
            ))

        
        users_list.sort(key=lambda x: x.risk_score, reverse=True)

        return {"users": users_list}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

def get_raw_data_from_db() -> dict:
    """ЗАГЛУШКА: Достаем сырые данные (accounts, services, transactions) из PostgreSQL."""
    
    import json
    with open("data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    return raw

def save_settings_to_db(settings: dict):
    """ЗАГЛУШКА: Сохранение весов в PostgreSQL"""
    pass

def save_scores_to_db(scores: list[dict]):
    """ЗАГЛУШКА: Сохранение скоринга в PostgreSQL"""
    pass

# --- 3. Новый эндпоинт ---
@app.post("/update-settings-and-score", tags=["Admin"])
def update_settings_and_score(req: UpdateSettingsRequest):
    try:
        # 1. Валидация настроек (пришли в json)
        cfg = ModelSettings(**req.settings)
        validate_settings(cfg)
        settings_dict = cfg.to_dict()

        save_settings_to_db(settings_dict)
        
        raw_data = get_raw_data_from_db()

        # 4. Пересчитываем скоринг
        snap = preprocess(raw_data)
        scored_df = score(snap, cfg)
        
        # Превращаем DataFrame в список словарей
        scores_list = scored_df.to_dict(orient="records")

        # 5. Сохраняем результаты скоринга в БД (Заглушка)
        save_scores_to_db(scores_list)

        return {
            "status": "success"
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Ошибка валидации: {str(ve)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл с сырыми данными не найден (в заглушке)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")