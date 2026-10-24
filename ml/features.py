import pandas as pd
from preprocess import Snapshot

EXPIRY_HORIZON_DAYS = 14

def _clamp01(x: pd.Series) -> pd.Series:
    return x.clip(0.0, 1.0)

def feat_no_autoprolong_share(s: Snapshot) -> pd.Series:
    """Доля активных услуг с отключенным автопродлением."""
    active = s.services[s.services.status.eq("active")]
    g = active.groupby("ownerId")["autoProlong"].apply(lambda x: (~x).mean())
    return _clamp01(g.reindex(s.accounts["id"]).fillna(0.0))

def feat_expiring_soon(s: Snapshot) -> pd.Series:
    """Насколько близко истекает ближайшая услуга (14 дней)."""
    active = s.services[s.services.status.eq("active") & 
                         s.services.days_to_expire.between(0, EXPIRY_HORIZON_DAYS)]
    m = active.groupby("ownerId")["days_to_expire"].min()
    return _clamp01(1.0 - m / EXPIRY_HORIZON_DAYS).reindex(s.accounts["id"]).fillna(0.0)

def feat_prolong_wait(s: Snapshot) -> pd.Series:
    """Есть ли услуги в статусе ожидания оплаты."""
    has = s.services[s.services.status.eq("prolong_wait")].groupby("ownerId").size()
    return (has.reindex(s.accounts["id"]).fillna(0) > 0).astype(float)

def feat_insufficient_funds(s: Snapshot) -> pd.Series:
    """Дефицит средств на оплату всех активных услуг"""
    svc = s.services[s.services.status.isin(["active", "prolong_wait"])]
    need = svc.groupby("ownerId")["price_eur"].sum()
    acc = s.accounts.set_index("id")["available_eur"]
    ratio = (need / acc.where(acc > 0, 1e-9)).reindex(s.accounts["id"]).fillna(0.0)
    return _clamp01(1.0 - 1.0 / ratio.clip(lower=1.0))

def feat_failed_prolong_share(s: Snapshot) -> pd.Series:
    """Доля неоплаченных продлений в истории клиента."""
    a = s.accounts
    return _clamp01((a["n_prolong_failed"] / a["n_prolong"].clip(lower=1)).fillna(0.0).set_axis(a["id"]))

def feat_low_replenishment(s: Snapshot) -> pd.Series:
    """Мало пополнял относительно медианы по всем клиентам."""
    x = s.accounts["totalReplenished_eur"]
    med = float(x.median()) or 1.0
    return _clamp01(1.0 - (x / med).clip(0, 1)).set_axis(s.accounts["id"])

# Реестр признаков: точка расширения
FEATURES = {
    "no_autoprolong_share": dict(fn=feat_no_autoprolong_share, weight=0.10, title="Отключено автопродление"),
    "expiring_soon":        dict(fn=feat_expiring_soon,        weight=0.50, title="Близко истекает услуга"),
    "prolong_wait":         dict(fn=feat_prolong_wait,         weight=0.15, title="Услуга ждёт оплаты"),
    "insufficient_funds":   dict(fn=feat_insufficient_funds,   weight=0.20, title="Не хватает средств"),
    "failed_prolong_share": dict(fn=feat_failed_prolong_share, weight=0.10, title="История неоплаченных продлений"),
    "low_replenishment":    dict(fn=feat_low_replenishment,    weight=0.05, title="Низкие пополнения"),
}