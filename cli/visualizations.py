from pathlib import Path
from typing import Optional, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pull_dada.y_finance.data_fetcher import YFinanceDataFetcher
from visualize_dada.chart_generator import ChartGenerator

console = Console()

class VisualizationManager:
    def __init__(self):
        self.chart_generator = ChartGenerator()
    
    def display_results(
        self,
        results: Dict,
        generate_charts: bool = True
    ):
        """Display fetch results and generate visualizations"""
        self._display_summary_panel(results)
        self._display_detailed_results(results, generate_charts)

    def _display_summary_panel(self, results: Dict):
        """Display summary panel with collection statistics"""
        total_success = sum(1 for result in results.values() if result['status'] == 'success')
        total_failed = len(results) - total_success
        
        base_dir = results[next(iter(results))]['paths']['ticker_dir'].parent if results else 'N/A'
        
        summary = f"""
[cyan]Collection Summary:[/cyan]
• Successfully processed: [green]{total_success}[/green] tickers
• Failed: [red]{total_failed}[/red] tickers
• Total files location: {base_dir}
        """
        console.print(Panel(summary, title="Summary", border_style="cyan"))

    def _display_detailed_results(self, results: Dict, generate_charts: bool):
        """Display detailed results table"""
        table = Table(
            title="Data Collection Results",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Ticker", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Files Generated", style="yellow")
        
        for ticker, result in results.items():
            if result['status'] == 'success':
                self._add_success_row(table, ticker, result, generate_charts)
            else:
                self._add_error_row(table, ticker, result)
        
        console.print("\n")
        console.print(table)

    def _add_success_row(self, table: Table, ticker: str, result: Dict, generate_charts: bool):
        """Add a success row to the results table"""
        data = result['data']
        paths = result['paths']
        
        if generate_charts:
            try:
                charts = self.chart_generator.generate_all_charts(
                    data,
                    ticker,
                    paths['ticker_dir']
                )
                files = [
                    f"Data: {paths['data_path'].name}",
                    f"Charts: {', '.join(f'{k}.html' for k in charts.keys())}"
                ]
                table.add_row(
                    ticker,
                    "[green]Success[/green]",
                    "\n".join(files)
                )
            except Exception as e:
                table.add_row(
                    ticker,
                    "[yellow]Partial Success[/yellow]",
                    f"Data saved, but chart generation failed: {str(e)}"
                )
        else:
            table.add_row(
                ticker,
                "[green]Success[/green]",
                f"Data: {paths['data_path'].name}"
            )

    def _add_error_row(self, table: Table, ticker: str, result: Dict):
        """Add an error row to the results table"""
        table.add_row(
            ticker,
            "[red]Error[/red]",
            result.get('message', 'Unknown error')
        )

    def display_intervals(self, fetcher: YFinanceDataFetcher):
        """Display supported intervals"""
        table = Table(
            title="Supported Data Intervals",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Interval", style="cyan")
        table.add_column("Period Available", style="green")
        table.add_column("Description", style="yellow")
        
        descriptions = {
            '1m': 'One minute intervals',
            '2m': 'Two minute intervals',
            '5m': 'Five minute intervals',
            '15m': 'Fifteen minute intervals',
            '30m': 'Thirty minute intervals',
            '60m': 'Hourly intervals',
            '90m': 'Ninety minute intervals',
            '1h': 'Hourly intervals',
            '1d': 'Daily intervals',
            '5d': 'Five day intervals',
            '1wk': 'Weekly intervals',
            '1mo': 'Monthly intervals',
            '3mo': 'Quarterly intervals'
        }
        
        for interval, period in fetcher.supported_intervals.items():
            table.add_row(
                interval,
                period,
                descriptions.get(interval, '')
            )
        
        console.print("\n")
        console.print(table) 