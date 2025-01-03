# Stock Universe

A powerful Python-based tool for fetching, analyzing, and visualizing stock market data using Yahoo Finance API. This tool provides an interactive command-line interface for downloading historical stock data and generating beautiful interactive charts.

## Key Features

- **Flexible Data Retrieval**
  - Support for multiple time intervals (1m to 3mo)
  - Smart date range selection based on interval limitations
  - Automatic rate limiting to prevent API throttling
  - Batch processing of multiple stock tickers

- **Interactive Charts**
  - Candlestick charts with volume data
  - Technical analysis indicators
  - Interactive zooming and panning
  - Hover tooltips with detailed information

- **User-Friendly Interface**
  - Interactive CLI with guided selections
  - Input validation and error handling
  - Progress tracking for long operations
  - Clear feedback and warnings

- **Data Management**
  - Organized data storage with timestamped directories
  - CSV exports for further analysis
  - Automatic handling of API limitations
  - Failed download retry mechanism

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HiNala/stock-universe.git
cd stock-universe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. Run the program:
```bash
python main.py
```

2. Follow the interactive prompts to:
   - Select stock tickers
   - Choose data frequency
   - Set date range
   - Configure visualization options

### Working with Tickers

You can input tickers in two ways:
1. **Input File**: Add tickers to `input_tickers/input_tickers.txt`
   ```
   # One ticker per line
   AAPL
   MSFT  # Comments supported
   GOOGL
   ```
2. **Manual Input**: Enter tickers directly when prompted (comma-separated)

### Data Intervals

| Interval | Description | Maximum History |
|----------|-------------|-----------------|
| 1m | One minute | 7 days |
| 2m, 5m, 15m, 30m, 60m, 1h | Intraday | 60 days |
| 1d | Daily | Max available |
| 5d | 5 day | Max available |
| 1wk | Weekly | Max available |
| 1mo | Monthly | Max available |
| 3mo | Quarterly | Max available |

### Output Structure

```
data/
└── YYYYMMDD_HHMMSS/          # Timestamp of run
    └── TICKER/               # One directory per ticker
        ├── data/             # Raw data
        │   └── TICKER_interval.csv
        └── charts/           # Interactive visualizations
            ├── TICKER_candlestick.html
            └── TICKER_technical.html
```

## Technical Details

- Built with Python 3.8+
- Uses yfinance for data retrieval
- Plotly for interactive visualizations
- Rich for beautiful CLI interface
- Type hints and documentation throughout

## Dependencies

Key packages:
- yfinance: Stock data retrieval
- plotly: Interactive charts
- pandas: Data manipulation
- rich: CLI interface
- typer: Command line parsing
- questionary: Interactive prompts

See `requirements.txt` for complete list with versions.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 