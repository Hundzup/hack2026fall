from dataclasses import dataclass
from datetime import datetime, timezone
import pandas as pd

@dataclass(frozen=True)
class Snapshot:
    accounts: pd.DataFrame
    services: pd.DataFrame
    transactions: pd.DataFrame
    now: pd.Timestamp
    raw: dict


def preprocess(raw: dict, now: datetime | None = None) -> Snapshot:
    """raw JSON -> Snapshot"""
    
    acc = pd.DataFrame(raw.get("accounts", []))
    if not acc.empty:
        for c in ("balance", "withdrawBalance", "totalReplenished", "bonusBalance"):
            acc[f"{c}_eur"] = acc[c] / 100.0
        
    
        acc["bonus_available_eur"] = acc["bonusBalance_eur"].where(
            acc["bonusState"].eq("unlocked"), 0.0
        )
        acc["available_eur"] = acc["balance_eur"] + acc["bonus_available_eur"]

    
    svc = pd.DataFrame(raw.get("services", []))
    if not svc.empty:
        svc["createdAt"] = pd.to_datetime(svc["createdAt"], utc=True)
        svc["expiresAt"] = pd.to_datetime(svc["expiresAt"], utc=True)
        svc["price_eur"] = svc["price"] / 100.0

    
    tx = pd.DataFrame(raw.get("transactions", []))
    if not tx.empty:
        tx["createdAt"] = pd.to_datetime(tx["createdAt"], utc=True)
        tx["amount_eur"] = tx["amount"] / 100.0
        tx["is_performed"] = tx["status"].eq("performed")
        tx["amount_paid_eur"] = tx["amount_eur"].where(tx["is_performed"], 0.0)
        tx["amount_failed_eur"] = tx["amount_eur"].where(~tx["is_performed"], 0.0)

    
    now_ts = pd.Timestamp(now or datetime.now(timezone.utc))
    if not svc.empty:
        svc["days_to_expire"] = (svc["expiresAt"] - now_ts).dt.total_seconds() / 86400.0

    
    if not svc.empty and not acc.empty:
        svc_per_acc = svc.groupby("ownerId").agg(
            n_services=("id", "count"),
            n_active=("status", lambda s: (s == "active").sum()),
            n_prolong_wait=("status", lambda s: (s == "prolong_wait").sum()),
            n_no_autoprolong=("autoProlong", lambda s: (~s).sum()),
            mrr_eur=("price_eur", "sum"),
        )
        acc = acc.merge(svc_per_acc, left_on="id", right_index=True, how="left")

    if not tx.empty and not svc.empty and not acc.empty:
        prolong = tx.query("type == 'prolong'").merge(
            svc[["id", "ownerId"]], left_on="serviceId", right_on="id", suffixes=("", "_svc")
        )
        prolong_stats = prolong.groupby("ownerId").agg(
            n_prolong=("id", "count"),
            n_prolong_failed=("is_performed", lambda s: int((~s).sum())),
        )
        acc = acc.merge(prolong_stats, left_on="id", right_index=True, how="left")

    if not acc.empty:
        acc = acc.fillna({
            "n_services": 0, "n_active": 0, "n_prolong_wait": 0, "n_no_autoprolong": 0,
            "mrr_eur": 0.0, "n_prolong": 0, "n_prolong_failed": 0
        })

    return Snapshot(accounts=acc, services=svc, transactions=tx, now=now_ts, raw=raw)