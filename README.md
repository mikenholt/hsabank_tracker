# HSA Bank Stock Performance TUI Tracker

This Python application dynamically tracks the performance of stocks based on a consolidated CSV file and displays results in a terminal-based UI (TUI). It also plots the total asset performance over time using an ASCII chart.

---

## Features
- **Dynamic Stock Tracking**: Tracks stock performance with updates every 5 minutes.
- **Rich Table Display**: Uses `rich` to display a visually appealing table of stock performance.
- **ASCII Chart for Total Assets**: Visualize total asset performance in real-time using `asciichartpy`.
- **Polling and Live Updates**: Automatically fetches stock data every 5 minutes until terminated or after 9 hours of runtime.
- **Graceful Exit**: Allows user to terminate the program with `Ctrl+C`.

---

## Installation

### Prerequisites
- HSA Bank investment transaction documents. To get these, follow these steps:
  1. Login to [https://account.hsabank.com](HSA Bank)
  2. Select **Manage Investments** in left nav bar
  3. Select **HSA Invest** if prompted
  4. Select **Documents** in top bar
  5. Use links to download each document listed. Store all files in a folder and copy its path  for use with the script.
- Python 3.8+
- Install the required Python packages:

```bash
pip install pandas yfinance rich asciichartpy
```

---

## Usage

### Prep data
To prep data, run the following command:

  ```bash
  python extract_data.py
  ```

Once complete, you should have an `extracted_data.csv` file in the project folder. This file tells the script which stocks to track.

To track performance, run:

  ```bash
  python track_stocks.py
  ```

---

## Columns in Table

- **Symbol:** The stock ticker symbol (e.g., AAPL, MSFT).
- **Qty:** The total quantity of shares held.
- **Avg Price:** The weighted average price of shares.
- **Current Price:** The latest price of the stock.
- **Last Day % / $:** Percentage and dollar change in the last day.
- **Last Week % / $:** Percentage and dollar change over the last week.
- **Last Month % / $:** Percentage and dollar change over the last month.
- **Total Asset:** The total value of the stock (Qty × Current Price).

---

## Example output

### Table
```plaintext
Stock Performance (Polling Every 5 Minutes)
+--------+-----+-----------+---------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Symbol | Qty | Avg Price | Current Price | Last Day %  | Last Day $  | Last Week % | Last Week $ | Last Month %| Last Month $| Total Asset |
+--------+-----+-----------+---------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| AAPL   | 10  | $150.50   | $155.00       | 3.00%       | $45.00      | 5.00%       | $75.00      | 8.00%       | $120.00     | $1,550.00   |
+--------+-----+-----------+---------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| TOTAL  |     |           |               | 4.00%       | $100.00     | 6.00%       | $180.00     | 9.00%       | $250.00     | $3,100.00   |
+--------+-----+-----------+---------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
```

### ASCII Chart
```plaintext
Total Asset History (ASCII Chart):
 1550.00 ┤      ╭─╮
 1500.00 ┤     ╭╯ ╰╮
 1450.00 ┤    ╭╯   ╰╮
 1400.00 ┤   ╭╯     ╰╮
 1350.00 ┤───╯       ╰───────────
 1300.00 ┤
```

---

## Development Notes

- The program fetches data using `yfinance`.
- The table and ASCII chart update every 60 seconds by default.
- If you want to customize polling speed, update the `POLLING_RATE` arg in `stock_performance.py`.
