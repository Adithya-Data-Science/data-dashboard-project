# Methodology

## Objective

Build a transparent fixed-income portfolio analytics workflow that compares baseline and optimized allocations across Treasury, TIPS, investment-grade, high-yield and broad bond exposures.

## Universe

The default investable universe is SHY, IEF, TLT, TIP, LQD, HYG and BND. These ETFs provide exposure to different duration, inflation and credit characteristics while keeping the project reproducible with public market data.

## Data preparation

Adjusted closing prices are downloaded at runtime with `yfinance`. Dates are sorted, duplicate observations are removed, assets are aligned, and daily prices are resampled to month-end. Monthly total returns are calculated from consecutive month-end prices.

## Capital-market inputs

Historical monthly returns are used to estimate:

- annualized arithmetic mean returns
- annualized covariance matrix
- asset correlation matrix

These are backward-looking sample estimates and are not treated as forecasts.

## Portfolio definitions

Three portfolios are constructed:

1. **Equal weight** - transparent baseline with identical allocation to each exposure.
2. **Minimum volatility** - minimizes `w' Sigma w` subject to weights summing to one, no shorting and a 35% maximum allocation per asset.
3. **Maximum Sharpe** - maximizes `(w' mu - rf) / sqrt(w' Sigma w)` under the same constraints.

Optimization uses SciPy SLSQP.

## Evaluation

Each portfolio is evaluated using:

- annualized return
- annualized volatility
- Sharpe ratio
- historical maximum drawdown
- allocation weights
- asset correlation matrix

The same monthly return history is used to calculate historical drawdown for all portfolios.

## Client analytics layer

`app.py` reads the generated CSV outputs and provides a Streamlit interface for portfolio comparison, allocation weights, correlations and interpretation notes. The dashboard is deliberately descriptive and avoids presenting historical optimization as a recommendation.

## Reproducibility

Run:

```bash
python portfolio_analytics.py --start 2012-01-01 --end 2026-01-01
streamlit run app.py
```

The first command regenerates all analytical outputs from the requested market-data window. The second launches the client-facing analytics interface.

## Limitations

Historical means and covariances are unstable, ETF histories and exposures differ, transaction costs and taxes are omitted, and optimization can be sensitive to small changes in inputs. This is an educational quantitative-research demonstration using public data, not investment advice and not a representation of PIMCO proprietary methods.
