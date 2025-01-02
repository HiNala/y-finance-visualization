# Y-Finance-isualization

A Python-based tool for fetching and visualizing stock market data using yfinance with interactive charts.

## Features

- Fetch historical stock data from Yahoo Finance
- Support for multiple time intervals (1m to 3mo)
- Interactive candlestick charts
- Technical analysis visualizations
- Flexible date range selection
- Batch processing of multiple tickers
- Rich CLI interface with real-time feedback

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HiNala/y-finance-isualization.git
cd y-finance-isualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Add stock tickers to `input_tickers/input_tickers.txt` or enter them manually when prompted.

2. Run the program:
```bash
python main.py
```

3. Follow the interactive prompts to:
   - Select stock tickers
   - Choose data frequency (1m, 5m, 1h, 1d, etc.)
   - Select date range
   - Enable/disable chart generation

4. Results will be saved in the `data` directory with the following structure:
```
data/
└── YYYYMMDD_HHMMSS/
    └── TICKER/
        ├── data/
        │   └── TICKER_interval.csv
        └── charts/
            ├── TICKER_candlestick.html
            └── TICKER_technical.html
```

## Data Intervals

- 1m: One minute data (last 7 days)
- 2m, 5m, 15m, 30m, 60m, 1h: Intraday data (last 60 days)
- 1d, 5d, 1wk, 1mo, 3mo: Historical data (max available)

## Requirements

- Python 3.8+
- See requirements.txt for package dependencies

## License

MIT License 