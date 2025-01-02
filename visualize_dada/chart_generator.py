import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

class ChartGenerator:
    def __init__(self):
        self.default_layout = {
            'template': 'plotly_dark',
            'title_x': 0.5,
            'showlegend': True,
            'height': 800,
            'margin': dict(t=100, l=50, r=50, b=50)
        }

    def create_candlestick_chart(
        self, 
        data: pd.DataFrame, 
        ticker: str,
        include_volume: bool = True
    ) -> go.Figure:
        """Create an interactive candlestick chart with volume"""
        rows = 2 if include_volume else 1
        fig = make_subplots(
            rows=rows, 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price', 'Volume') if include_volume else (f'{ticker} Price',),
            row_width=[0.7, 0.3] if include_volume else [1]
        )

        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        # Add volume bar chart
        if include_volume and 'Volume' in data.columns:
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(data['Close'], data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=2, col=1
            )

        # Update layout
        layout = self.default_layout.copy()
        layout.update(
            title_text=f"{ticker} Stock Price and Volume",
            xaxis_rangeslider_visible=False
        )
        fig.update_layout(**layout)

        return fig

    def create_technical_analysis_chart(
        self, 
        data: pd.DataFrame, 
        ticker: str,
        ma_periods: list = [20, 50, 200]
    ) -> go.Figure:
        """Create a technical analysis chart with moving averages"""
        # Calculate moving averages
        for period in ma_periods:
            data[f'MA{period}'] = data['Close'].rolling(window=period).mean()

        fig = self.create_candlestick_chart(data, ticker)

        # Add moving averages
        for period in ma_periods:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[f'MA{period}'],
                    name=f'{period}-day MA',
                    line=dict(width=1)
                ),
                row=1, col=1
            )

        return fig

    def save_chart(
        self, 
        fig: go.Figure, 
        ticker: str, 
        ticker_dir: Path,
        chart_type: str
    ) -> Path:
        """Save chart as HTML file in the charts directory"""
        charts_dir = ticker_dir / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = charts_dir / f"{ticker}_{chart_type}.html"
        fig.write_html(str(file_path))
        return file_path

    def generate_all_charts(
        self,
        data: pd.DataFrame,
        ticker: str,
        ticker_dir: Path
    ) -> Dict[str, Path]:
        """Generate and save all chart types for a ticker"""
        charts = {}
        
        # Basic candlestick chart
        candlestick_fig = self.create_candlestick_chart(data, ticker)
        charts['candlestick'] = self.save_chart(
            candlestick_fig, 
            ticker, 
            ticker_dir, 
            'candlestick'
        )
        
        # Technical analysis chart
        ta_fig = self.create_technical_analysis_chart(data, ticker)
        charts['technical'] = self.save_chart(
            ta_fig, 
            ticker, 
            ticker_dir, 
            'technical'
        )
        
        return charts 