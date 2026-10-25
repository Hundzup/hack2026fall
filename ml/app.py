from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
import pandas as pd
import psycopg2
import json
from psycopg2.extras import execute_values
from schemas import AnalyzeRequest, AnalyzeResponse, UsersRiskResponse, UserRiskMetrics
from schemas import UpdateSettingsRequest
from preprocess import preprocess
from scoring import ModelSettings, score, validate_settings
from money import expected_loss


DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "hackathon_db"
DB_USER = "postgres"
DB_PASS = "postgres"


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
    """
    Сохраняет веса каждой фичи в отдельную строку таблицы model_weights.
    Сохраняет глобальные пороги в model_thresholds.
    """
    weights = settings.get("weights", {})
    low_max = float(settings.get("low_max", 0.2))
    high_min = float(settings.get("high_min", 0.3))

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cursor = conn.cursor()

        # 1. СОХРАНЕНИЕ ВЕСОВ (Upsert для каждой фичи)
        if weights:
            # Подготавливаем данные для пакетной вставки: [(name, weight), ...]
            weight_data = [(k, float(v)) for k, v in weights.items()]
            
            upsert_weights_query = """
                INSERT INTO model_weights (feature_name, weight)
                VALUES %s
                ON CONFLICT (feature_name) DO UPDATE SET
                    weight = EXCLUDED.weight,
                    updated_at = CURRENT_TIMESTAMP;
            """
            # execute_values делает один быстрый запрос на все фичи сразу
            execute_values(cursor, upsert_weights_query, weight_data)

            # 2. УДАЛЕНИЕ УСТАРЕВШИХ ФИЧЕЙ (которых нет в текущем запросе)
            # Это нужно, если вы удалили признак из features.py
            feature_names = list(weights.keys())
            delete_stale_query = "DELETE FROM model_weights WHERE feature_name NOT IN %s;"
            cursor.execute(delete_stale_query, (tuple(feature_names),))

        # 3. СОХРАНЕНИЕ ПОРОГОВ
        upsert_thresholds_query = """
            INSERT INTO model_thresholds (id, low_max, high_min)
            VALUES (1, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                low_max = EXCLUDED.low_max,
                high_min = EXCLUDED.high_min,
                updated_at = CURRENT_TIMESTAMP;
        """
        cursor.execute(upsert_thresholds_query, (low_max, high_min))

        conn.commit()
        print(f"[DB] Успешно сохранено {len(weights)} весов и пороги модели.")

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"[DB ERROR] Не удалось сохранить настройки: {e}")
        raise e
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def save_scores_to_db(scores: list[dict]):
    """
    Сохраняет (или обновляет) результаты скоринга в таблице customers.
    Использует UPSERT (INSERT ON CONFLICT UPDATE).
    """
    if not scores:
        return

    # SQL-запрос для UPSERT
    # Если customer_id уже есть в базе, мы обновляем его метрики.
    # Если нет (новый клиент), то вставляем новую строку.
    query = """
        INSERT INTO customers (
            customer_id, email, balance_eur, total_replenished_eur, 
            risk_score, risk_level, reasons
        ) VALUES %s
        ON CONFLICT (customer_id) DO UPDATE SET
            email = EXCLUDED.email,
            balance_eur = EXCLUDED.balance_eur,
            total_replenished_eur = EXCLUDED.total_replenished_eur,
            risk_score = EXCLUDED.risk_score,
            risk_level = EXCLUDED.risk_level,
            reasons = EXCLUDED.reasons;
    """

    # Подготавливаем данные в виде кортежей для execute_values
    values = []
    for row in scores:
        values.append((
            int(row["customer_id"]),
            str(row["email"]),
            float(row["balance_eur"]),
            float(row["total_replenished_eur"]),
            float(row["risk_score"]),
            str(row["risk_level"]),
            # ВАЖНО: колонка reasons имеет тип jsonb. 
            # psycopg2 ожидает строку, поэтому используем json.dumps
            json.dumps(row["reasons"], ensure_ascii=False)
        ))

    try:
        # Подключаемся к БД
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cursor = conn.cursor()

        # execute_values делает один быстрый запрос на всю пачку данных
        execute_values(cursor, query, values)
        
        conn.commit()
        print(f"[DB] Успешно сохранено/обновлено {len(scores)} записей в таблице customers.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback() # Откатываем транзакцию в случае ошибки
        print(f"[DB ERROR] Не удалось сохранить скор: {e}")
        raise e
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    

@app.post("/update-settings", tags=["Admin"])
def update_settings_and_score(req: UpdateSettingsRequest):
    try:
        
        cfg = ModelSettings(**req.settings)
        validate_settings(cfg)
        settings_dict = cfg.to_dict()

        save_settings_to_db(settings_dict)
        
        
        raw_data = get_raw_data_from_db()

        
        snap = preprocess(raw_data)
        scored_df = score(snap, cfg)
        
        
        acc_info = snap.accounts[["id", "email", "balance_eur", "totalReplenished_eur"]]
        full_df = scored_df.merge(
            acc_info, 
            left_on="customer_id", 
            right_on="id", 
            how="left"
        )

        # Превращаем DataFrame в список словарей
        scores_list = full_df.to_dict(orient="records")

        # 5. Сохраняем в БД (вызываем нашу новую функцию)
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