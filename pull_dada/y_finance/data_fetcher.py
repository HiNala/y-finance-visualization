import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
import time
from typing import List, Dict, Optional, Tuple

class YFinanceDataFetcher:
    def __init__(self):
        self.supported_intervals = {
            '1m': '7d',    # 1 minute data available for last 7 days
            '2m': '60d',   # 2 minute data available for last 60 days
            '5m': '60d',
            '15m': '60d',
            '30m': '60d',
            '60m': '60d',
            '90m': '60d',
            '1h': '60d',
            '1d': 'max',   # daily data available for entire history
            '5d': 'max',
            '1wk': 'max',
            '1mo': 'max',
            '3mo': 'max'
        }
        self.last_request_time = None
        self.min_request_interval = 0.5  # Minimum time between requests in seconds

    def _rate_limit(self):
        """Implement rate limiting between requests"""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def fetch_data(
        self, 
        ticker: str, 
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data for a single ticker
        Args:
            ticker: Stock symbol
            interval: Data interval (e.g., '1d', '1h', '5m')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        if interval not in self.supported_intervals:
            raise ValueError(f"Unsupported interval: {interval}")
        
        self._rate_limit()
        
        try:
            stock = yf.Ticker(ticker)
            
            # Handle date range based on interval limitations
            if start_date and end_date:
                # For minute-level data, ensure we don't exceed the maximum period
                if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '1h']:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    max_days = 7 if interval == '1m' else 60
                    
                    # If requested period exceeds limit, adjust start date
                    if (end - start).days > max_days:
                        start_date = (end - timedelta(days=max_days)).strftime("%Y-%m-%d")
                        print(f"Note: Adjusted start date to {start_date} due to {interval} interval limitations")
                
                data = stock.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )
            else:
                # If no dates provided, use default period
                data = stock.history(
                    period=self.supported_intervals[interval],
                    interval=interval
                )
            
            if data.empty:
                print(f"Warning: No data returned for {ticker}")
                return None
                
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def save_data(
        self, 
        data: pd.DataFrame, 
        ticker: str, 
        base_dir: Path,
        interval: str
    ) -> Dict[str, Path]:
        """Save fetched data to CSV in organized directory structure"""
        # Create ticker directory with data and charts subdirectories
        ticker_dir = base_dir / ticker
        data_dir = ticker_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save data file
        file_name = f"{ticker}_{interval}.csv"
        data_path = data_dir / file_name
        data.to_csv(data_path)
        
        return {
            'ticker_dir': ticker_dir,
            'data_path': data_path
        }

    def process_tickers(self, ticker_input: str) -> List[str]:
        """Process comma-separated ticker input"""
        return [t.strip().upper() for t in ticker_input.split(',') if t.strip()]

    def fetch_and_save_multiple(
        self, 
        ticker_input: str, 
        base_dir: Path,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Fetch and save data for multiple tickers
        Args:
            ticker_input: Comma-separated string of tickers
            base_dir: Base directory for saving data
            interval: Data interval
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        Returns:
            Dictionary with results for each ticker
        """
        tickers = self.process_tickers(ticker_input)
        results = {}
        
        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            data = self.fetch_data(ticker, interval, start_date, end_date)
            
            if data is not None:
                try:
                    paths = self.save_data(data, ticker, base_dir, interval)
                    results[ticker] = {
                        'status': 'success',
                        'paths': paths,
                        'data': data
                    }
                    print(f"Successfully saved data for {ticker}")
                except Exception as e:
                    results[ticker] = {
                        'status': 'error',
                        'message': f"Error saving data: {str(e)}"
                    }
            else:
                results[ticker] = {
                    'status': 'error',
                    'message': f"Failed to fetch data"
                }
        
        return results 