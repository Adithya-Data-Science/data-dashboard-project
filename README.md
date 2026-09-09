# Fixed-Income Portfolio Optimization & Client Analytics

A reproducible quantitative research project that builds and compares fixed-income portfolios across U.S. Treasury, inflation-linked, investment-grade, high-yield and broad bond exposures. The project is designed around the same core problems handled in institutional client analytics: asset allocation, portfolio construction, diversification, risk/return trade-offs and communicating portfolio implications clearly.

## Research question

How do different fixed-income allocation rules change expected return, volatility, diversification and drawdown characteristics, and how can those results be presented in a client-ready analytics workflow?

## Skills demonstrated

- Asset allocation and constrained portfolio optimization
- Portfolio construction and diversification analysis
- Expected return and covariance estimation
- Minimum-volatility and maximum-Sharpe portfolios
- Risk/return, drawdown and correlation analysis
- Python, Pandas, NumPy, SciPy, yfinance and Streamlit
- Reproducible research and client-facing communication

## Investable universe

| Ticker | Exposure |
| --- | --- |
| SHY | 1-3 Year U.S. Treasuries |
| IEF | 7-10 Year U.S. Treasuries |
| TLT | 20+ Year U.S. Treasuries |
| TIP | U.S. TIPS |
| LQD | Investment-grade corporate bonds |
| HYG | High-yield corporate bonds |
| BND | Broad U.S. investment-grade bonds |

Market prices are downloaded at runtime with `yfinance`; raw vendor data is not committed to the repository.

## Start-to-finish workflow

1. **Define the investment universe** - choose fixed-income exposures with different duration, inflation and credit characteristics.
2. **Acquire market data** - download adjusted closing prices for the full universe.
3. **Validate the data** - sort dates, remove duplicate observations, align assets and report missing values before analysis.
4. **Transform prices into returns** - convert daily prices to month-end observations and calculate monthly total returns.
5. **Estimate capital-market inputs** - annualize historical mean returns and the covariance matrix.
6. **Construct portfolios** - build equal-weight, minimum-volatility and maximum-Sharpe portfolios under long-only allocation constraints.
7. **Evaluate portfolio risk and performance** - calculate annualized return, volatility, Sharpe ratio and historical maximum drawdown.
8. **Analyze diversification** - compare asset correlations and optimized weights to explain where risk is concentrated.
9. **Publish client analytics** - export machine-readable results and expose them through an interactive Streamlit application.
10. **Document limitations** - identify sensitivity to the estimation window, historical-data bias and the fact that optimized weights are not forecasts or investment advice.

## Portfolio methods

For asset return vector `mu`, covariance matrix `Sigma` and weights `w`:

- Expected portfolio return: `w' mu`
- Portfolio volatility: `sqrt(w' Sigma w)`
- Sharpe ratio: `(portfolio return - risk-free rate) / volatility`
- Minimum-volatility portfolio: minimize `w' Sigma w`
- Maximum-Sharpe portfolio: maximize the Sharpe ratio

Constraints require weights to sum to 100%, prohibit short positions and cap each individual exposure at 35%.

## Repository structure

```text
.
├── portfolio_analytics.py      # data acquisition, optimization and exported results
├── app.py                      # interactive client analytics dashboard
├── METHODOLOGY.md              # formulas, assumptions and validation rules
├── requirements.txt
├── outputs/                    # generated weights, metrics and correlation matrix
└── README.md
```

## Run the analysis

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python portfolio_analytics.py --start 2012-01-01 --end 2026-01-01
```

Then launch the client analytics interface:

```bash
streamlit run app.py
```

## Generated outputs

The analysis writes:

- `outputs/portfolio_weights.csv`
- `outputs/portfolio_metrics.csv`
- `outputs/correlation_matrix.csv`
- `outputs/monthly_returns.csv`
- `outputs/summary.json`

These outputs are generated from the requested market-data window rather than hard-coded into the project.

## Interpretation

This project is intentionally focused on research process and portfolio construction rather than claiming that an optimized historical portfolio will outperform in the future. Historical mean/covariance estimates are unstable, ETF histories differ, transaction costs and taxes are omitted, and the exercise does not use PIMCO proprietary data or models.

## Resume-ready description

**Fixed-Income Portfolio Optimization & Client Analytics | Python, Pandas, NumPy, SciPy, Streamlit**

Built a reproducible fixed-income allocation framework across Treasury, TIPS and credit exposures; estimated risk/return inputs and constructed equal-weight, minimum-volatility and maximum-Sharpe portfolios under diversification constraints. Developed an interactive client-analytics interface comparing portfolio weights, correlations, annualized risk/return, Sharpe ratio and drawdown while documenting estimation and model limitations.
