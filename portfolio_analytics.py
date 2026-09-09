from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parent
TICKERS = ["SHY", "IEF", "TLT", "TIP", "LQD", "HYG", "BND"]


def annualized_stats(monthly_returns: pd.DataFrame):
    mu = monthly_returns.mean() * 12
    cov = monthly_returns.cov() * 12
    return mu, cov


def portfolio_metrics(weights, mu, cov, rf=0.02):
    w = np.asarray(weights)
    ret = float(w @ mu.values)
    vol = float(np.sqrt(w @ cov.values @ w))
    sharpe = (ret - rf) / vol if vol > 0 else np.nan
    return ret, vol, sharpe


def optimize_min_vol(mu, cov, cap=0.35):
    n = len(mu)
    x0 = np.repeat(1 / n, n)
    bounds = [(0.0, cap)] * n
    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    obj = lambda w: portfolio_metrics(w, mu, cov)[1]
    res = minimize(obj, x0, bounds=bounds, constraints=cons, method="SLSQP")
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def optimize_max_sharpe(mu, cov, cap=0.35, rf=0.02):
    n = len(mu)
    x0 = np.repeat(1 / n, n)
    bounds = [(0.0, cap)] * n
    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    obj = lambda w: -portfolio_metrics(w, mu, cov, rf)[2]
    res = minimize(obj, x0, bounds=bounds, constraints=cons, method="SLSQP")
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def historical_drawdown(monthly_returns, weights):
    p = monthly_returns.mul(weights, axis=1).sum(axis=1)
    wealth = (1 + p).cumprod()
    dd = wealth / wealth.cummax() - 1
    return float(dd.min())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2012-01-01")
    p.add_argument("--end", default="2026-01-01")
    p.add_argument("--rf", type=float, default=0.02)
    args = p.parse_args()

    raw = yf.download(TICKERS, start=args.start, end=args.end, auto_adjust=True, progress=False)["Close"]
    raw = raw.sort_index().loc[~raw.index.duplicated()].dropna(how="all")
    monthly = raw.resample("ME").last().pct_change(fill_method=None).dropna(how="any")
    mu, cov = annualized_stats(monthly)

    equal = np.repeat(1 / len(TICKERS), len(TICKERS))
    min_vol = optimize_min_vol(mu, cov)
    max_sharpe = optimize_max_sharpe(mu, cov, rf=args.rf)
    portfolios = {"equal_weight": equal, "minimum_volatility": min_vol, "maximum_sharpe": max_sharpe}

    weights_df = pd.DataFrame(portfolios, index=mu.index)
    rows = []
    for name, weights in portfolios.items():
        ret, vol, sharpe = portfolio_metrics(weights, mu, cov, args.rf)
        rows.append({
            "portfolio": name,
            "annualized_return": ret,
            "annualized_volatility": vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": historical_drawdown(monthly, weights),
        })
    metrics = pd.DataFrame(rows).set_index("portfolio")

    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    weights_df.to_csv(out / "portfolio_weights.csv")
    metrics.to_csv(out / "portfolio_metrics.csv")
    monthly.corr().to_csv(out / "correlation_matrix.csv")
    monthly.to_csv(out / "monthly_returns.csv")
    summary = {
        "start": args.start,
        "end": args.end,
        "tickers": TICKERS,
        "risk_free_rate": args.rf,
        "observations": int(len(monthly)),
        "best_historical_sharpe": metrics["sharpe_ratio"].idxmax(),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(metrics.round(4))
    print("\nWeights:\n", weights_df.round(4))


if __name__ == "__main__":
    main()
