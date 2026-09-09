from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"

st.set_page_config(page_title="Fixed-Income Client Analytics", layout="wide")
st.title("Fixed-Income Portfolio Optimization & Client Analytics")
st.caption("Research demonstration using public market data; not investment advice.")

required = [OUT / "portfolio_metrics.csv", OUT / "portfolio_weights.csv", OUT / "correlation_matrix.csv"]
if not all(p.exists() for p in required):
    st.warning("Run `python portfolio_analytics.py` first to generate the analytics outputs.")
    st.stop()

metrics = pd.read_csv(OUT / "portfolio_metrics.csv", index_col=0)
weights = pd.read_csv(OUT / "portfolio_weights.csv", index_col=0)
corr = pd.read_csv(OUT / "correlation_matrix.csv", index_col=0)

st.subheader("Portfolio comparison")
st.dataframe(metrics.style.format({
    "annualized_return": "{:.2%}",
    "annualized_volatility": "{:.2%}",
    "sharpe_ratio": "{:.2f}",
    "max_drawdown": "{:.2%}",
}), use_container_width=True)

st.subheader("Allocation weights")
st.bar_chart(weights)
st.dataframe(weights.style.format("{:.1%}"), use_container_width=True)

st.subheader("Asset correlation matrix")
st.dataframe(corr.style.format("{:.2f}"), use_container_width=True)

st.subheader("How to interpret")
st.markdown("""
- **Equal weight** is a transparent diversification baseline.
- **Minimum volatility** emphasizes the covariance structure and seeks the lowest estimated portfolio risk under the allocation constraints.
- **Maximum Sharpe** balances estimated return and risk relative to the supplied risk-free rate.
- Historical optimized weights are sensitive to the sample window and should not be interpreted as forecasts or recommendations.
""")
