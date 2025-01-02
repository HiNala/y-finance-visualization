import typer
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from rich.console import Console
from rich.table import Table
import sys
from datetime import datetime, timedelta
import questionary
from dateutil import parser
from dateutil.relativedelta import relativedelta

from pull_dada.y_finance.data_fetcher import YFinanceDataFetcher
from cli.visualizations import VisualizationManager

app = typer.Typer(no_args_is_help=False)
console = Console()

def get_data_directory() -> Path:
    """Create and return the data directory with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = Path("data") / timestamp
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def read_ticker_file() -> List[str]:
    """Read tickers from input_tickers.txt file"""
    ticker_file = Path("input_tickers") / "input_tickers.txt"
    tickers = []
    
    with open(ticker_file, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove inline comments and clean up
                ticker = line.split('#')[0].strip()
                if ticker:
                    tickers.append(ticker)
    
    return tickers

def check_input_file() -> bool:
    """Check if input tickers file exists and has valid content"""
    ticker_file = Path("input_tickers") / "input_tickers.txt"
    if ticker_file.exists():
        tickers = read_ticker_file()
        return len(tickers) > 0
    return False

def get_tickers() -> str:
    """Get tickers from file or manual input"""
    has_input_file = check_input_file()
    
    if has_input_file:
        file_tickers = read_ticker_file()
        console.print("\n[cyan]Available tickers in input file:[/cyan]")
        console.print(", ".join(file_tickers))
        
        use_file = questionary.confirm(
            "Would you like to use tickers from the input file?",
            default=True
        ).ask()
        
        if use_file:
            return ", ".join(file_tickers)
    else:
        console.print("\n[yellow]No input file found or file is empty. Please enter tickers manually.[/yellow]")
    
    return questionary.text(
        "Enter stock tickers (comma-separated)",
        validate=lambda text: len(text.strip()) > 0
    ).ask()

def get_interval_selection() -> str:
    """Get data frequency selection interactively"""
    intervals = [
        ('1m', 'One minute intervals - Last 7 days'),
        ('2m', 'Two minute intervals - Last 60 days'),
        ('5m', 'Five minute intervals - Last 60 days'),
        ('15m', 'Fifteen minute intervals - Last 60 days'),
        ('30m', 'Thirty minute intervals - Last 60 days'),
        ('60m', 'Hourly intervals - Last 60 days'),
        ('1h', 'Hourly intervals - Last 60 days'),
        ('1d', 'Daily intervals'),
        ('5d', 'Five day intervals'),
        ('1wk', 'Weekly intervals'),
        ('1mo', 'Monthly intervals'),
        ('3mo', 'Quarterly intervals')
    ]
    
    choices = [f"{interval} ({desc})" for interval, desc in intervals]
    
    # Find the index of the '1d' option
    default_index = next(
        (i for i, (interval, _) in enumerate(intervals) if interval == '1d'),
        0
    )
    
    selection = questionary.select(
        "Select data frequency:",
        choices=choices,
        default=choices[default_index]
    ).ask()
    
    # Extract the interval code from the selection
    return selection.split()[0]

def get_date_range(interval: str) -> Tuple[str, str]:
    """Get date range based on interval"""
    end_date = datetime.now()
    
    # Define interval-specific ranges
    interval_ranges = {
        '1m': ["Last 7 days"],
        '2m': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '5m': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '15m': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '30m': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '60m': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '1h': ["Last 7 days", "Last 30 days", "Last 60 days"],
        '1d': [
            "Last 7 days",
            "Last 30 days",
            "Last 3 months",
            "Last 6 months",
            "Last 1 year",
            "Last 5 years",
            "Custom range"
        ],
        '5d': [
            "Last 30 days",
            "Last 3 months",
            "Last 6 months",
            "Last 1 year",
            "Last 5 years",
            "Custom range"
        ],
        '1wk': [
            "Last 3 months",
            "Last 6 months",
            "Last 1 year",
            "Last 5 years",
            "Custom range"
        ],
        '1mo': [
            "Last 6 months",
            "Last 1 year",
            "Last 5 years",
            "Custom range"
        ],
        '3mo': [
            "Last 1 year",
            "Last 5 years",
            "Custom range"
        ]
    }
    
    # Get available ranges for selected interval
    ranges = interval_ranges.get(interval, ["Last 1 year", "Custom range"])
    
    range_choice = questionary.select(
        "Select date range:",
        choices=ranges
    ).ask()
    
    if range_choice == "Custom range":
        # Get custom date range
        start_date_str = questionary.text(
            "Enter start date (YYYY-MM-DD):",
            validate=lambda text: bool(try_parse_date(text))
        ).ask()
        
        end_date_str = questionary.text(
            "Enter end date (YYYY-MM-DD or press enter for today):",
            validate=lambda text: not text or bool(try_parse_date(text))
        ).ask()
        
        start_date = parser.parse(start_date_str)
        end_date = parser.parse(end_date_str) if end_date_str else end_date
        
    else:
        # Calculate start date based on selection
        if range_choice == "Last 7 days":
            start_date = end_date - timedelta(days=7)
        elif range_choice == "Last 30 days":
            start_date = end_date - timedelta(days=30)
        elif range_choice == "Last 3 months":
            start_date = end_date - relativedelta(months=3)
        elif range_choice == "Last 6 months":
            start_date = end_date - relativedelta(months=6)
        elif range_choice == "Last 1 year":
            start_date = end_date - relativedelta(years=1)
        elif range_choice == "Last 5 years":
            start_date = end_date - relativedelta(years=5)
        else:
            return None, None
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def try_parse_date(date_str: str) -> Optional[datetime]:
    """Try to parse a date string"""
    try:
        return parser.parse(date_str)
    except:
        return None

def get_user_inputs() -> Tuple[str, str, Tuple[str, str], bool]:
    """Get all user inputs in sequence"""
    console.print("\n[bold cyan]Stock Universe - Data Collection[/bold cyan]")
    
    # Step 1: Get tickers
    console.print("\n[bold cyan]Step 1: Stock Selection[/bold cyan]")
    tickers = get_tickers()
    
    # Step 2: Select data frequency
    console.print("\n[bold cyan]Step 2: Data Frequency Selection[/bold cyan]")
    interval = get_interval_selection()
    
    # Step 3: Select date range
    console.print("\n[bold cyan]Step 3: Date Range Selection[/bold cyan]")
    start_date, end_date = get_date_range(interval)
    
    # Step 4: Confirm visualization
    console.print("\n[bold cyan]Step 4: Visualization Options[/bold cyan]")
    generate_charts = questionary.confirm(
        "Would you like to generate interactive charts?",
        default=True
    ).ask()
    
    return tickers, interval, (start_date, end_date), generate_charts

def display_summary(tickers: str, interval: str, date_range: Tuple[str, str], generate_charts: bool):
    """Display summary of user selections"""
    console.print("\n[bold cyan]Summary of Selections[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Parameter", style="yellow")
    table.add_column("Value", style="green")
    
    table.add_row("Stocks", str(tickers))
    table.add_row("Data Frequency", str(interval))
    if date_range[0] and date_range[1]:
        table.add_row("Date Range", f"{date_range[0]} to {date_range[1]}")
    else:
        table.add_row("Date Range", "Maximum available")
    table.add_row("Generate Charts", "Yes" if generate_charts else "No")
    
    console.print(table)

def fetch_data(tickers: str, interval: str, date_range: Tuple[str, str], generate_charts: bool):
    """Core function to fetch data and generate visualizations"""
    try:
        # Display summary and confirm
        display_summary(tickers, interval, date_range, generate_charts)
        if not questionary.confirm("Proceed with these selections?", default=True).ask():
            console.print("[yellow]Operation cancelled by user. Exiting...[/yellow]")
            return
        
        # Initialize components
        data_fetcher = YFinanceDataFetcher()
        viz_manager = VisualizationManager()
        
        # Create data directory
        data_dir = get_data_directory()
        console.print(f"\n[green]Created data directory: {data_dir}[/green]")
        
        # Fetch data and display results
        results = data_fetcher.fetch_and_save_multiple(
            tickers, 
            data_dir, 
            interval,
            start_date=date_range[0],
            end_date=date_range[1]
        )
        viz_manager.display_results(results, generate_charts)
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

def main():
    """Entry point for the application"""
    try:
        # Get user inputs
        tickers, interval, date_range, generate_charts = get_user_inputs()
        # Fetch and process data
        fetch_data(tickers, interval, date_range, generate_charts)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user. Exiting...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    main()