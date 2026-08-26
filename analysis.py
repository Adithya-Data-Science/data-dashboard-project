"""Leakage-aware equity factor analysis and return-prediction pipeline.

Data source:
https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv
"""

from pathlib import Path
import json
import urllib.request

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv"
RAW_PATH = DATA_DIR / "all_stocks_5yr.csv"
FEATURES = [
    "ret_1d", "mom_5d", "mom_21d", "mom_63d",
    "vol_21d", "vol_63d", "volume_z_21d", "intraday_range",
]


def download_data() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not RAW_PATH.exists():
        print("Downloading public OHLCV dataset...")
        urllib.request.urlretrieve(DATA_URL, RAW_PATH)


def build_panel() -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(RAW_PATH, parse_dates=["date"])
    raw.columns = raw.columns.str.lower()
    raw = raw.sort_values(["name", "date"]).drop_duplicates(["name", "date"])
    raw = raw.dropna(subset=["date", "name", "close", "volume"])
    raw = raw[(raw["close"] > 0) & (raw["volume"] >= 0)].copy()

    # Select 120 relatively liquid names using only the training-era period.
    selection_period = raw[raw["date"] < "2017-01-01"].copy()
    selection_period["dollar_volume"] = (
        selection_period["close"] * selection_period["volume"]
    )
    liquid_names = (
        selection_period.groupby("name")["dollar_volume"]
        .median().nlargest(120).index
    )
    df = raw[raw["name"].isin(liquid_names)].copy()
    g = df.groupby("name", group_keys=False)

    df["ret_1d"] = g["close"].pct_change()
    df["mom_5d"] = g["close"].pct_change(5)
    df["mom_21d"] = g["close"].pct_change(21)
    df["mom_63d"] = g["close"].pct_change(63)
    df["vol_21d"] = g["ret_1d"].rolling(21).std().reset_index(level=0, drop=True)
    df["vol_63d"] = g["ret_1d"].rolling(63).std().reset_index(level=0, drop=True)
    volume_mean = g["volume"].rolling(21).mean().reset_index(level=0, drop=True)
    volume_std = g["volume"].rolling(21).std().reset_index(level=0, drop=True)
    df["volume_z_21d"] = (df["volume"] - volume_mean) / volume_std
    df["intraday_range"] = (df["high"] - df["low"]) / df["close"]
    df["target_5d"] = g["close"].shift(-5) / df["close"] - 1

    panel = df.dropna(subset=FEATURES + ["target_5d"]).copy()
    summary = {
        "raw_rows": int(len(raw)),
        "raw_tickers": int(raw["name"].nunique()),
        "panel_rows": int(len(panel)),
        "panel_tickers": int(panel["name"].nunique()),
        "start_date": str(panel["date"].min().date()),
        "end_date": str(panel["date"].max().date()),
    }
    return panel, summary


def daily_rank_ic(frame: pd.DataFrame) -> float:
    values = []
    for _, day in frame.groupby("date"):
        if len(day) >= 20 and day["prediction"].nunique() > 1:
            corr = spearmanr(day["prediction"], day["target_5d"]).statistic
            if np.isfinite(corr):
                values.append(corr)
    return float(np.mean(values))


def quintile_spread(frame: pd.DataFrame) -> pd.Series:
    def one_day(day: pd.DataFrame) -> float:
        if len(day) < 50 or day["prediction"].nunique() < 5:
            return np.nan
        ranks = day["prediction"].rank(method="first")
        q = pd.qcut(ranks, 5, labels=False)
        return day.loc[q == 4, "target_5d"].mean() - day.loc[q == 0, "target_5d"].mean()

    return frame.groupby("date").apply(one_day, include_groups=False).dropna()


def evaluate(model, split: pd.DataFrame, label: str) -> tuple[dict, pd.DataFrame]:
    out = split[["date", "name", "target_5d"]].copy()
    out["prediction"] = model.predict(split[FEATURES])
    errors = out["target_5d"] - out["prediction"]
    baseline = out["target_5d"] - out["target_5d"].mean()
    spread = quintile_spread(out)
    metrics = {
        "split": label,
        "rows": int(len(out)),
        "r2": float(1 - np.square(errors).sum() / np.square(baseline).sum()),
        "mae": float(errors.abs().mean()),
        "mean_daily_rank_ic": daily_rank_ic(out),
        "mean_5d_quintile_spread": float(spread.mean()),
        "quintile_spread_positive_days": float((spread > 0).mean()),
    }
    return metrics, out


def main() -> None:
    download_data()
    RESULTS_DIR.mkdir(exist_ok=True)
    panel, summary = build_panel()

    train = panel[panel["date"] < "2017-01-01"]
    validation = panel[(panel["date"] >= "2017-01-01") & (panel["date"] < "2017-07-01")]
    test = panel[panel["date"] >= "2017-07-01"]

    candidates = {}
    for alpha in [0.1, 1.0, 10.0, 100.0]:
        model = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=alpha)),
        ])
        model.fit(train[FEATURES], train["target_5d"])
        metrics, _ = evaluate(model, validation, f"validation_alpha_{alpha:g}")
        candidates[alpha] = (model, metrics)

    best_alpha = max(
        candidates,
        key=lambda a: candidates[a][1]["mean_daily_rank_ic"],
    )
    selected_model = candidates[best_alpha][0]
    validation_metrics, _ = evaluate(selected_model, validation, "validation")
    test_metrics, predictions = evaluate(selected_model, test, "test")

    coefficients = pd.DataFrame({
        "feature": FEATURES,
        "standardized_coefficient": selected_model.named_steps["ridge"].coef_,
    }).sort_values("standardized_coefficient", key=np.abs, ascending=False)
    coefficients.to_csv(RESULTS_DIR / "coefficients.csv", index=False)
    predictions.to_csv(RESULTS_DIR / "test_predictions.csv", index=False)
    pd.DataFrame([validation_metrics, test_metrics]).to_csv(
        RESULTS_DIR / "metrics.csv", index=False
    )

    report = {
        "dataset": summary,
        "split_rows": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
        },
        "selected_ridge_alpha": best_alpha,
        "validation": validation_metrics,
        "test": test_metrics,
        "limitations": [
            "Historical constituents create survivorship bias.",
            "Prices are not explicitly adjusted for corporate actions.",
            "The test window is short because the public dataset ends in 2018.",
            "The quintile spread is diagnostic and excludes transaction costs.",
        ],
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
