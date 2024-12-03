import pandas as pd
import yfinance as yf
from rich.table import Table
from rich.console import Console
from rich.text import Text
from time import sleep, time
import asciichartpy

POLLING_RATE = 60  # seconds

def fetch_stock_performance(symbol, quantity):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")  # Fetch up to one month's data
        if hist.empty:
            return {
                "Current Price": "N/A",
                "Last Day $": 0,
                "Last Day %": 0,
                "Last Week $": 0,
                "Last Week %": 0,
                "Last Month $": 0,
                "Last Month %": 0,
                "Total Asset": "N/A",
            }

        current_price = hist['Close'][-1]
        last_day_perf = {
            "%": ((hist['Close'][-1] - hist['Close'][-2]) / hist['Close'][-2]) * 100 if len(hist) > 1 else 0,
            "$": (hist['Close'][-1] - hist['Close'][-2]) * quantity if len(hist) > 1 else 0,
        }
        last_week_perf = {
            "%": ((hist['Close'][-1] - hist['Close'][-6]) / hist['Close'][-6]) * 100 if len(hist) > 5 else 0,
            "$": (hist['Close'][-1] - hist['Close'][-6]) * quantity if len(hist) > 5 else 0,
        }
        last_month_perf = {
            "%": ((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100 if len(hist) > 1 else 0,
            "$": (hist['Close'][-1] - hist['Close'][0]) * quantity if len(hist) > 1 else 0,
        }

        total_asset = current_price * quantity if isinstance(current_price, (float, int)) else "N/A"

        return {
            "Current Price": current_price,
            "Last Day $": last_day_perf["$"],
            "Last Day %": last_day_perf["%"],
            "Last Week $": last_week_perf["$"],
            "Last Week %": last_week_perf["%"],
            "Last Month $": last_month_perf["$"],
            "Last Month %": last_month_perf["%"],
            "Total Asset": total_asset,
        }
    except Exception:
        return {
            "Current Price": "Error",
            "Last Day $": 0,
            "Last Day %": 0,
            "Last Week $": 0,
            "Last Week %": 0,
            "Last Month $": 0,
            "Last Month %": 0,
            "Total Asset": "Error",
        }


def style_performance(value, is_currency=False):
    if isinstance(value, (float, int)):
        color = "green" if value > 0 else "red"
        if is_currency:
            return Text(f"${value:.2f}", style=color)
        return Text(f"{value:.2f}%", style=color)
    return Text(value)


def display_performance_table(consolidated_file, polling_rate=POLLING_RATE):
    df = pd.read_csv(consolidated_file)
    console = Console()
    start_time = time()
    total_assets_history = []  # Store historical total asset values

    while True:
        table = Table(title=f"Stock Performance (Refreshing Every {polling_rate} Seconds)", show_lines=True)
        table.add_column("Symbol", style="cyan", justify="center")
        table.add_column("Qty", justify="right")
        table.add_column("Avg Price", justify="right")
        table.add_column("Current Price", justify="right")
        table.add_column("Last Day %", justify="right")
        table.add_column("Last Day $", justify="right")
        table.add_column("Last Week %", justify="right")
        table.add_column("Last Week $", justify="right")
        table.add_column("Last Month %", justify="right")
        table.add_column("Last Month $", justify="right")
        table.add_column("Total Asset", justify="right")

        total_assets_sum = 0
        total_last_day_change = 0
        total_last_week_change = 0
        total_last_month_change = 0
        total_assets_weight_day = 0
        total_assets_weight_week = 0
        total_assets_weight_month = 0

        for _, row in df.iterrows():
            symbol = row['Symbol']
            quantity = row['Total Quantity']
            performance = fetch_stock_performance(symbol, quantity)

            total_asset = performance["Total Asset"]
            if isinstance(total_asset, (float, int)):
                total_assets_sum += total_asset
                total_last_day_change += performance["Last Day $"]
                total_last_week_change += performance["Last Week $"]
                total_last_month_change += performance["Last Month $"]
                if performance["Last Day %"] != 0:
                    total_assets_weight_day += total_asset * performance["Last Day %"]
                if performance["Last Week %"] != 0:
                    total_assets_weight_week += total_asset * performance["Last Week %"]
                if performance["Last Month %"] != 0:
                    total_assets_weight_month += total_asset * performance["Last Month %"]

            table.add_row(
                symbol,
                f"{quantity:.2f}",
                f"${row['Weighted Average Price']:.2f}",
                Text(f"${performance['Current Price']:.2f}" if isinstance(performance["Current Price"], float) else performance["Current Price"]),
                style_performance(performance["Last Day %"]),
                style_performance(performance["Last Day $"], is_currency=True),
                style_performance(performance["Last Week %"]),
                style_performance(performance["Last Week $"], is_currency=True),
                style_performance(performance["Last Month %"]),
                style_performance(performance["Last Month $"], is_currency=True),
                style_performance(total_asset, is_currency=True),
            )

        total_last_day_percentage = total_assets_weight_day / total_assets_sum if total_assets_sum > 0 else 0
        total_last_week_percentage = total_assets_weight_week / total_assets_sum if total_assets_sum > 0 else 0
        total_last_month_percentage = total_assets_weight_month / total_assets_sum if total_assets_sum > 0 else 0

        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            "",
            "",
            style_performance(total_last_day_percentage),
            style_performance(total_last_day_change, is_currency=True),
            style_performance(total_last_week_percentage),
            style_performance(total_last_week_change, is_currency=True),
            style_performance(total_last_month_percentage),
            style_performance(total_last_month_change, is_currency=True),
            style_performance(total_assets_sum, is_currency=True),
        )

        console.clear()
        console.print(table)

        # Append total assets to history
        total_assets_history.append(total_assets_sum)

        # Display ASCII chart
        console.print("\n[bold]Total Asset Trend (Last 10 Points)[/bold]")
        console.print(asciichartpy.plot(total_assets_history[-10:], {"height": 10}))

        if time() - start_time >= 9 * 3600:
            console.print("\nProgram has been running for 9 hours. Exiting...\n")
            break

        console.print("\nPress Ctrl+C to quit.")
        try:
            sleep(polling_rate)
        except KeyboardInterrupt:
            console.print("\nPolling stopped. Exiting...\n")
            break


if __name__ == "__main__":
    consolidated_file = "consolidated_by_symbol.csv"
    display_performance_table(consolidated_file)
