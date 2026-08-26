# Equity Factor Analysis and Return Prediction

This project tests whether simple trailing price, volatility, volume, and
intraday-range factors contain cross-sectional information about U.S. equities'
next five trading-day returns.

The emphasis is on research hygiene: a training-era liquidity screen,
chronological train/validation/test splits, lagged features, a simple regularized
baseline, and honest reporting of weak or negative findings.

## Project structure

```text
.
├── analysis.py
├── equity_factor_analysis.ipynb
├── METHODOLOGY.md
├── README.md
├── requirements.txt
└── results/
    ├── coefficients.csv
    ├── metrics.csv
    └── summary.json
```

## Reproduce the analysis

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python analysis.py
```

The data downloads automatically from
[Plotly's public datasets repository](https://github.com/plotly/datasets/blob/master/all_stocks_5yr.csv).
The raw file is intentionally excluded from version control.

## Data, features, and evaluation

- Public daily OHLCV data covering more than 500 S&P 500 names
- A 120-stock liquid subset selected using training-era median dollar volume
- Momentum, realized-volatility, standardized-volume, and intraday-range features
- A five-trading-day forward-return target
- Chronological training, validation, and untouched test periods
- Ridge regularization selected by validation-period daily rank correlation

See [METHODOLOGY.md](METHODOLOGY.md) for the full research design, leakage
controls, definitions, and limitations.

## Out-of-sample results

The cleaned 120-stock panel contains **141,333 stock-day observations**. The
untouched test period contains 17,640 observations.

| Test metric | Result |
| --- | ---: |
| R-squared | -0.0159 |
| MAE | 0.0237 |
| Mean daily Spearman rank IC | -0.0108 |
| Mean top-minus-bottom quintile five-day return | -0.00018 |
| Days with a positive quintile spread | 51.0% |

The main finding is that these simple technical factors did **not** produce
stable out-of-sample return prediction. That negative result is retained rather
than hidden: it demonstrates why chronological testing and untouched test data
matter. Exact machine-readable values are stored in `results/`.

## Responsible interpretation

The dataset has survivorship and corporate-action limitations, and the test
window is short. Quintile spreads exclude costs and execution constraints.
Results should be interpreted as an educational cross-sectional prediction
study rather than investment advice.
