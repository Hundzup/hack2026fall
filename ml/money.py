import pandas as pd
from preprocess import Snapshot

STATUS_BOOST = {"active": 0.0, "suspended": 0.1, "prolong_wait": 0.4, "blocked": 0.6, "deleted": 1.0}

def expected_loss(s: Snapshot, scored: pd.DataFrame) -> pd.DataFrame:
    p_cust = scored.set_index("customer_id")["risk_score"]
    svc = s.services.copy()
    
    # Вероятность оттока услуги
    svc["p_churn"] = (svc["ownerId"].map(p_cust).fillna(0.0) + svc["status"].map(STATUS_BOOST)).clip(0, 1)

    # Сколько денег платформа НЕ получит (Цена минус то, что уже на балансе)
    avail = s.accounts.set_index("id")["available_eur"]
    svc = svc.join(avail.rename("available_eur"), on="ownerId")
    
    svc["funded_eur"] = (
        svc["available_eur"]
        .div(svc.groupby("ownerId")["price_eur"].transform("sum"))
        .mul(svc["price_eur"])
    ).clip(upper=svc["price_eur"]).fillna(0.0)
    
    svc["exposure_eur"] = (svc["price_eur"] - svc["funded_eur"]).clip(lower=0.0)
    svc["expected_loss_eur"] = svc["p_churn"] * svc["exposure_eur"]
    
    return svc[["id", "ownerId", "status", "price_eur", "funded_eur", "exposure_eur", "p_churn", "expected_loss_eur"]]