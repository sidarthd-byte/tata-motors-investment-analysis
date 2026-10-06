# ============================================================
# Tata Motors - Personal Investment Analysis
# Educational analysis - NOT investment advice
# ============================================================

!pip -q install --upgrade yfinance

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from IPython.display import display

os.makedirs("charts", exist_ok=True)
os.makedirs("data", exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (8, 4.5),
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False
})

# ---------------- SETTINGS ----------------
STOCK = "TMPV.NS"
BENCHMARK = "^NSEI"

PEERS = {
    "Maruti Suzuki": "MARUTI.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Hyundai Motor India": "HYUNDAI.NS"
}

INVESTMENT = 100000

DEMERGER_FACTOR = None
DEMERGER_DATE = "2025-10-14"

MANUAL = {}
MANUAL_PE = {}

# ============================================================
# STEP 1 - FINANCIALS
# ============================================================

CR = 1e7

tk = yf.Ticker(STOCK)
inc = tk.financials
bal = tk.balance_sheet


def row(df, names):
    for name in names:
        if name in df.index:
            return df.loc[name]
    return pd.Series(np.nan, index=df.columns)


def by_year(series):
    series = series.copy()
    series.index = pd.to_datetime(series.index).year
    return series


px_all = yf.download(
    STOCK,
    period="max",
    auto_adjust=True,
    progress=False
)["Close"].squeeze()


fin = pd.DataFrame({
    "revenue": by_year(
        row(inc, ["Total Revenue", "Operating Revenue"])
    ) / CR,

    "net_profit": by_year(
        row(inc, ["Net Income Common Stockholders", "Net Income"])
    ) / CR,

    "eps": by_year(
        row(inc, ["Diluted EPS", "Basic EPS"])
    ),

    "total_debt": by_year(
        row(bal, ["Total Debt"])
    ) / CR,

    "equity": by_year(
        row(bal, ["Stockholders Equity", "Common Stock Equity"])
    ) / CR,

    "current_assets": by_year(
        row(bal, ["Current Assets"])
    ) / CR,

    "current_liabilities": by_year(
        row(bal, ["Current Liabilities"])
    ) / CR
}).sort_index()

fin.index = ["FY" + str(y) for y in fin.index]
fin = fin.dropna(subset=["revenue", "net_profit"])


for fy, values in MANUAL.items():
    for key, value in values.items():
        fin.loc[fy, key] = value


def fy_price(fy):
    date = pd.Timestamp(int(fy[2:]), 3, 31)
    series = px_all[px_all.index <= date]

    if len(series):
        return float(series.iloc[-1])

    return np.nan


fin["year_end_price"] = [fy_price(fy) for fy in fin.index]

fin["roe"] = (
    fin["net_profit"] /
    fin["equity"] *
    100
)

fin.to_csv("data/tata_motors_financials.csv")

print("Years found on Yahoo:", list(fin.index))
display(fin.round(2))


# ============================================================
# STEP 2 - GROWTH + RATIOS
# ============================================================

calc = pd.DataFrame(index=fin.index)

calc["Revenue (Rs cr)"] = fin["revenue"]
calc["Revenue Growth %"] = fin["revenue"].pct_change() * 100
calc["Net Profit (Rs cr)"] = fin["net_profit"]
calc["Net Profit Growth %"] = fin["net_profit"].pct_change() * 100
calc["EPS (Rs)"] = fin["eps"]
calc["Total Debt (Rs cr)"] = fin["total_debt"]
calc["ROE %"] = fin["roe"]


ratios = pd.DataFrame(index=fin.index)

ratios["Profit Margin %"] = (
    fin["net_profit"] /
    fin["revenue"] *
    100
)

ratios["ROE %"] = fin["roe"]

ratios["Debt-to-Equity"] = (
    fin["total_debt"] /
    fin["equity"]
)

ratios["Current Ratio"] = (
    fin["current_assets"] /
    fin["current_liabilities"]
)

ratios["P/E"] = (
    fin["year_end_price"] /
    fin["eps"]
)

print("\n=== FINANCIAL PERFORMANCE ===")
display(calc.T.round(2))

print("=== RATIOS ===")
display(ratios.T.round(2))

calc.to_csv("data/calculated_metrics.csv")
ratios.to_csv("data/ratios.csv")


# ============================================================
# STEP 3 - CHARTS
# ============================================================

def bar_chart(series, title, ylabel, filename, fmt="{:,.0f}"):
    series = series.dropna()

    if series.empty:
        print("Skipped:", title)
        return

    fig, ax = plt.subplots()

    bars = ax.bar(series.index, series.values)

    for bar, value in zip(bars, series.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            fmt.format(value),
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)

    fig.tight_layout()
    fig.savefig("charts/" + filename, dpi=150)
    plt.show()


bar_chart(
    fin["revenue"],
    "Tata Motors - Revenue",
    "Rs crore",
    "revenue.png"
)

bar_chart(
    fin["net_profit"],
    "Tata Motors - Net Profit",
    "Rs crore",
    "net_profit.png"
)

bar_chart(
    fin["eps"],
    "Tata Motors - EPS",
    "Rs per share",
    "eps.png",
    "{:,.2f}"
)

bar_chart(
    fin["total_debt"],
    "Tata Motors - Total Debt",
    "Rs crore",
    "debt.png"
)

bar_chart(
    fin["roe"],
    "Tata Motors - ROE (calculated)",
    "%",
    "roe.png",
    "{:,.1f}"
)


# ============================================================
# STEP 4 - STOCK VS NIFTY 50
# ============================================================

raw = yf.download(
    [STOCK, BENCHMARK],
    period="6y",
    auto_adjust=True,
    progress=False
)["Close"]

prices = raw.rename(
    columns={
        STOCK: "Tata Motors",
        BENCHMARK: "NIFTY 50"
    }
).dropna()


if DEMERGER_FACTOR is not None:
    prices.loc[
        prices.index < DEMERGER_DATE,
        "Tata Motors"
    ] *= DEMERGER_FACTOR


chg = prices["Tata Motors"].pct_change()

if chg.min() < -0.30:
    print(
        f"\nWARNING: one-day drop of {chg.min():.0%} "
        f"on {chg.idxmin().date()} - likely the demerger. "
        "Returns across this date are UNRELIABLE until "
        "you set DEMERGER_FACTOR."
    )
else:
    print("\nNo suspicious price cliff found.")


prices.to_csv("data/stock_prices.csv")


def period_return(series, years):
    start = series[
        series.index <=
        series.index[-1] - pd.DateOffset(years=years)
    ]

    if start.empty:
        return np.nan

    return (
        (series.iloc[-1] - start.iloc[-1]) /
        start.iloc[-1] *
        100
    )


rows = []

for years in [1, 3, 5]:
    tata_return = period_return(
        prices["Tata Motors"],
        years
    )

    nifty_return = period_return(
        prices["NIFTY 50"],
        years
    )

    rows.append({
        "Period": f"{years} Year",
        "Tata Motors %": tata_return,
        "NIFTY 50 %": nifty_return,
        "Outperformance (pts)": tata_return - nifty_return
    })


returns = pd.DataFrame(rows).set_index("Period")

print("=== STOCK RETURNS ===")
display(returns.round(1))

returns.to_csv("data/stock_returns.csv")


five = prices[
    prices.index >=
    prices.index[-1] - pd.DateOffset(years=5)
]

(
    five / five.iloc[0] * 100
).plot()

plt.title(
    "Tata Motors vs NIFTY 50 (rebased to 100)",
    fontweight="bold"
)

plt.ylabel("Index (start = 100)")
plt.tight_layout()

plt.savefig(
    "charts/stock_vs_nifty.png",
    dpi=150
)

plt.show()


# ============================================================
# STEP 5 - COMPETITORS + P/E VALUATION
# ============================================================

def snapshot(name, ticker):
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        info = {}

    return {
        "Company": name,
        "Ticker": ticker,
        "Industry": info.get("industry"),

        "Market Cap (Rs cr)": (
            info.get("marketCap") or np.nan
        ) / CR,

        "Revenue (Rs cr)": (
            info.get("totalRevenue") or np.nan
        ) / CR,

        "Net Profit (Rs cr)": (
            info.get("netIncomeToCommon") or np.nan
        ) / CR,

        "P/E": MANUAL_PE.get(
            name,
            info.get("trailingPE")
        )
    }


all_companies = {
    "Tata Motors": STOCK,
    **PEERS
}

comp = pd.DataFrame(
    [
        snapshot(name, ticker)
        for name, ticker in all_companies.items()
    ]
).set_index("Company")

print("\n=== COMPETITOR TABLE ===")
display(comp.round(1))

comp.to_csv("data/competitor_data.csv")


tata_pe = comp.loc["Tata Motors", "P/E"]

avg_peer_pe = (
    comp.drop("Tata Motors")["P/E"]
    .dropna()
    .mean()
)


if pd.notna(tata_pe) and pd.notna(avg_peer_pe):
    diff = (tata_pe / avg_peer_pe - 1) * 100

    label = "PREMIUM" if diff > 0 else "DISCOUNT"

    print(
        f"Tata P/E {tata_pe:.1f} vs peer average "
        f"{avg_peer_pe:.1f} -> {label} of {abs(diff):.0f}%"
    )

    ax = comp["P/E"].plot(
        kind="bar",
        rot=15
    )

    ax.axhline(
        avg_peer_pe,
        ls="--",
        label="Peer average"
    )

    ax.legend()
    ax.set_title("P/E Comparison", fontweight="bold")
    ax.set_ylabel("P/E (x)")

    plt.tight_layout()
    plt.savefig("charts/pe_comparison.png", dpi=150)
    plt.show()

else:
    print(
        "P/E missing - fill MANUAL_PE from "
        "Screener.in / NSE and re-run."
    )


# ============================================================
# STEP 6 - Rs 1,00,000 SCENARIO
# ============================================================

price_now = float(prices["Tata Motors"].iloc[-1])

whole = int(INVESTMENT // price_now)

cash_left = INVESTMENT - whole * price_now

print(f"\n=== Rs {INVESTMENT:,} SCENARIO ===")

print(
    f"Share price (last close "
    f"{prices.index[-1].date()}): "
    f"Rs {price_now:,.2f}"
)

print(
    f"Exact shares: {INVESTMENT / price_now:.2f} | "
    f"Whole shares: {whole} | "
    f"Cash left: Rs {cash_left:,.2f}"
)


scen = []

for label, change in [
    ("Rises 10%", 0.10),
    ("Rises 20%", 0.20),
    ("Falls 10%", -0.10),
    ("Falls 20%", -0.20)
]:
    value = (
        whole *
        price_now *
        (1 + change) +
        cash_left
    )

    scen.append({
        "Scenario": label,
        "Portfolio Value (Rs)": value,
        "Gain/Loss (Rs)": value - INVESTMENT
    })


scen = pd.DataFrame(scen).set_index("Scenario")

display(scen.round(0))

print("HYPOTHETICAL SCENARIOS - NOT FORECASTS.")

scen.to_csv("data/scenario.csv")


# ============================================================
# STEP 7 - SCORECARD
# ============================================================

def score(value, cuts, higher=True):
    if pd.isna(value):
        return np.nan

    if higher:
        return (
            5 if value >= cuts[0]
            else 4 if value >= cuts[1]
            else 3 if value >= cuts[2]
            else 2 if value >= cuts[3]
            else 1
        )

    return (
        5 if value < cuts[0]
        else 4 if value < cuts[1]
        else 3 if value < cuts[2]
        else 2 if value < cuts[3]
        else 1
    )


n = len(fin) - 1

if n > 0 and fin["revenue"].iloc[0] > 0:
    cagr = (
        (
            fin["revenue"].iloc[-1] /
            fin["revenue"].iloc[0]
        ) ** (1 / n) - 1
    ) * 100
else:
    cagr = np.nan


m = ratios["Profit Margin %"].iloc[-1]
de = ratios["Debt-to-Equity"].iloc[-1]
o3 = returns.loc["3 Year", "Outperformance (pts)"]


if (
    pd.notna(tata_pe)
    and pd.notna(avg_peer_pe)
    and avg_peer_pe != 0
):
    rel = tata_pe / avg_peer_pe
else:
    rel = np.nan


card = pd.DataFrame(
    {
        "Score": [
            score(cagr, [15, 10, 5, 0]),
            score(m, [8, 5, 3, 1]),
            score(de, [0.5, 1, 1.5, 2.5], False),
            score(o3, [20, 5, -5, -20]),
            score(rel, [0.7, 0.9, 1.1, 1.4], False)
        ],

        "Reasoning": [
            f"Revenue CAGR {cagr:.1f}% over {n} yrs",
            f"Latest net margin {m:.1f}%",
            f"Latest debt-to-equity {de:.2f}",
            f"3-yr outperformance {o3:+.1f} pts vs NIFTY",
            f"P/E = {rel:.2f}x peer average"
        ]
    },

    index=[
        "Financial performance",
        "Profitability",
        "Debt/leverage",
        "Stock performance",
        "Relative valuation"
    ]
)

print("\n=== SCORECARD ===")
display(card)

overall = card["Score"].mean()

print(
    f"Overall: {overall:.1f}/5 "
    f"({int(card['Score'].notna().sum())} of 5 areas scored)"
)


card["Score"].dropna()[::-1].plot(
    kind="barh",
    xlim=(0, 5),
    figsize=(8, 3.5)
)

plt.title(
    f"Investment Scorecard - Overall {overall:.1f}/5",
    fontweight="bold"
)

plt.xlabel("1 = weak, 5 = strong")

plt.tight_layout()

plt.savefig(
    "charts/scorecard.png",
    dpi=150
)

plt.show()

card.to_csv("data/scorecard.csv")


# ============================================================
# STEP 8 - CONCLUSION
# ============================================================

verdict = (
    "Attractive"
    if overall >= 3.5
    else "Neutral"
    if overall >= 2.5
    else "Less Attractive"
)

print(
    f"\nVERDICT (simple educational analysis): "
    f"{verdict.upper()} | NOT investment advice."
)

print(
    "Limitations: demerger breaks comparability; "
    "Yahoo data may differ from filings; "
    "P/E is a simple measure."
)

print(
    "Past performance does not guarantee future returns."
)


# ============================================================
# DOWNLOAD EVERYTHING
# ============================================================

!zip -rq analysis_outputs.zip charts data

try:
    from google.colab import files
    files.download("analysis_outputs.zip")
except Exception:
    pass
