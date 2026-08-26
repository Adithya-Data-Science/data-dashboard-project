# Methodology

## Research question

Can trailing price, volatility, volume, and intraday-range features provide
cross-sectional information about U.S. equities' next five trading-day returns?

## Data and universe

The pipeline downloads the public `all_stocks_5yr.csv` dataset maintained in
Plotly's datasets repository. It contains daily OHLCV observations for more
than 500 historical S&P 500 names from 2013 through early 2018.

To keep the project substantial but credible for an early-career portfolio,
the analysis selects 120 equities by median dollar volume measured strictly
before 2017. This prevents validation or test-period liquidity from determining
the research universe.

## Features and target

All features use information available on or before date *t*:

- 1-, 5-, 21-, and 63-day returns
- 21- and 63-day realized volatility
- 21-day standardized volume
- intraday high-low range divided by closing price

The target is the close-to-close return from *t* through *t+5*. Rows lacking a
complete lookback or forward target are removed.

## Evaluation design

- Training: observations before January 1, 2017
- Validation: January through June 2017
- Test: July 2017 through the end of the dataset

Four Ridge penalties are compared only on validation-period mean daily rank
correlation. The selected specification is then evaluated once on the untouched
test period. Reported metrics are out-of-sample R-squared, MAE, mean daily
Spearman rank correlation, and the average next-five-day return difference
between predicted top and bottom quintiles.

## Reproducibility

Run `python analysis.py` from the repository root. The script downloads the
data, reconstructs every feature, selects the model, and writes machine-readable
metrics, coefficients, and test predictions to `results/`.

## Limitations

This is an educational research project, not a live trading claim. The dataset
uses a historical constituent list and therefore may contain survivorship bias.
Prices are not explicitly adjusted for splits or dividends, the final test
window is short, and the diagnostic quintile spread excludes turnover,
transaction costs, capacity, and execution constraints.
