# Tata Motors Personal Investment Analysis

An educational finance project that analyzes Tata Motors using basic financial-performance, valuation, stock-performance, and hypothetical investment-scenario metrics.

> **Disclaimer:** This project is for educational purposes only and is **not investment advice**.

## What the project analyzes

- Revenue and revenue growth
- Net profit and net profit growth
- EPS
- Total debt
- ROE
- Profit margin
- Debt-to-equity ratio
- Current ratio
- Historical P/E
- Tata Motors vs NIFTY 50 performance
- Peer comparison
- P/E comparison with peers
- A hypothetical ₹1,00,000 investment scenario
- A simple rule-based investment scorecard

## Data source

The script retrieves market and financial data using **Yahoo Finance through `yfinance`**.

Because financial databases can contain incomplete or differently classified figures, the results should be checked against company filings and other authoritative sources before being used for any serious analysis.

## Project structure

```text
tata-motors-investment-analysis/
│
├── tata_motors_analysis.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── data/
│   └── (generated CSV files)
│
└── charts/
    └── (generated PNG charts)
```

## Run in Google Colab

The easiest method is:

1. Open Google Colab.
2. Upload `tata_motors_analysis.py`.
3. Open the file.
4. Copy the code into a Colab code cell.
5. Run the cell.

The script installs `yfinance` automatically when run in Colab.

## Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python tata_motors_analysis.py
```

## Outputs

The script creates:

### CSV files

- `tata_motors_financials.csv`
- `calculated_metrics.csv`
- `ratios.csv`
- `stock_prices.csv`
- `stock_returns.csv`
- `competitor_data.csv`
- `scenario.csv`
- `scorecard.csv`

### Charts

- Revenue
- Net profit
- EPS
- Total debt
- ROE
- Tata Motors vs NIFTY 50
- P/E comparison
- Investment scorecard

## Important limitation

Tata Motors underwent a demerger, which can affect historical price and financial comparability. The script therefore includes a demerger warning and an optional `DEMERGER_FACTOR` setting.

Do not treat the generated score or verdict as a recommendation to buy or sell the stock.

## Educational objective

The purpose of this project is to demonstrate how basic financial-analysis concepts can be combined into a simple investment-analysis dashboard for a hypothetical ₹1,00,000 investment.
