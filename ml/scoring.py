from dataclasses import dataclass, field, asdict
import numpy as np
import pandas as pd
from preprocess import Snapshot
from features import FEATURES

@dataclass(frozen=True)
class ModelSettings:
    weights: dict[str, float] = field(default_factory=lambda: {
        n: m["weight"] for n, m in FEATURES.items()
    })
    low_max: float = 0.33
    high_min: float = 0.66

    def to_dict(self) -> dict:
        return asdict(self)

def validate_settings(s: ModelSettings) -> None:
    unknown = set(s.weights) - set(FEATURES)
    if unknown:
        raise ValueError(f"unknown features: {sorted(unknown)}")
    if any(w < 0 for w in s.weights.values()):
        raise ValueError("weights must be >= 0")
    if sum(s.weights.values()) <= 0:
        raise ValueError("sum of weights must be > 0")
    if not (0.0 <= s.low_max < s.high_min <= 1.0):
        raise ValueError("need 0 <= low_max < high_min <= 1")

def score(snap: Snapshot, cfg: ModelSettings) -> pd.DataFrame:
    ids = snap.accounts["id"].reset_index(drop=True)
    
    # Собираем матрицу признаков
    feats_df = pd.DataFrame(
        {n: m["fn"](snap).reindex(ids.values).fillna(0.0).values for n, m in FEATURES.items()},
        index=ids.values,
    )
    
    
    w = pd.Series({n: cfg.weights.get(n, FEATURES[n]["weight"]) for n in feats_df.columns}, dtype=float)
    print(w)
    wsum = float(w.sum()) or 1.0
    
    
    contrib = feats_df.mul(w, axis=1)
    total_score = contrib.sum(axis=1) / wsum
    
    
    level = pd.cut(total_score, bins=[-np.inf, cfg.low_max, cfg.high_min, np.inf], labels=["low", "medium", "high"])

    def top_reasons(row):
        top = row.sort_values(ascending=False).head(3)
        return [
            {"feature": k, "contribution": round(float(v), 4), "title": FEATURES[k]["title"]}
            for k, v in top.items() if v > 0
        ]

    return pd.DataFrame({
        "customer_id": total_score.index,
        "risk_score": total_score.round(4).values,
        "risk_level": level.astype(str).values,
        "reasons": [top_reasons(contrib.loc[i]) for i in contrib.index],
    })