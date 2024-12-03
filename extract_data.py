import os
import pandas as pd
from PyPDF2 import PdfReader

DEFAULT_PATH = "./hsabank_pdfs/"

def extract_stock_data(pdf_path):
    reader = PdfReader(pdf_path)
    data = []

    for page in reader.pages:
        lines = page.extract_text().split('\n')
        i = 0
        while i < len(lines):
            # Look for the start of a transaction (assume a valid ticker line)
            if lines[i].isupper() and len(lines[i]) <= 5:  # Likely a stock ticker
                try:
                    symbol = lines[i]  # Ticker
                    company = lines[i + 1]  # Company Name
                    action = lines[i + 3]  # Action (Buy/Sell)

                    # Check if the next line is Execution Time
                    if ":" in lines[i + 4]:  # Likely an Execution Time
                        execution_time = lines[i + 4]
                        quantity = float(lines[i + 5])
                        price = float(lines[i + 6])
                        trade_date = lines[i + 7]
                        settle_date = lines[i + 8]
                        capacity = lines[i + 9]
                        skip_lines = 10  # Number of lines to skip
                    else:  # No Execution Time
                        execution_time = None
                        quantity = float(lines[i + 4])
                        price = float(lines[i + 5])
                        trade_date = lines[i + 6]
                        settle_date = lines[i + 7]
                        capacity = lines[i + 8]
                        skip_lines = 9  # Number of lines to skip

                    # Add the data to the list
                    data.append({
                        "Symbol": symbol,
                        "Company": company,
                        "Action": action,
                        "Execution Time": execution_time,
                        "Quantity": quantity,
                        "Price": price,
                        "Trade Date": trade_date,
                        "Settle Date": settle_date,
                        "Capacity": capacity,
                        "Source File": os.path.basename(pdf_path),
                    })

                    # Skip ahead by the number of lines processed
                    i += skip_lines
                except (IndexError, ValueError):  # Handle any incomplete/malformed entries
                    i += 1
            else:
                i += 1
    return data

def process_pdf_directory(directory_path):
    all_data = []  # Consolidated data across all PDFs

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, file_name)
            print(f"Processing file: {file_name}")
            stock_data = extract_stock_data(pdf_path)

            if stock_data:
                all_data.extend(stock_data)  # Append data to the consolidated list

    return all_data

def consolidate_by_symbol(dataframe):
    """Group by Symbol and compute weighted average price."""
    grouped = dataframe.groupby('Symbol').apply(
        lambda group: pd.Series({
            'Total Quantity': group['Quantity'].sum(),
            'Weighted Average Price': (group['Price'] * group['Quantity']).sum() / group['Quantity'].sum()
        })
    ).reset_index()

    return grouped

# Ask the user for the directory path, defaulting to DEFAULT_PATH if no input is given
pdf_dir = input(f"Enter the path to the directory containing PDFs (default: {DEFAULT_PATH}): ").strip() or DEFAULT_PATH

# Process all PDFs in the directory
print(f"Processing all PDFs in directory: {pdf_dir}")
all_stock_data = process_pdf_directory(pdf_dir)

# Convert to a DataFrame
df = pd.DataFrame(all_stock_data)

# Display the consolidated DataFrame
print("\nConsolidated Stock Data:")
print(df)

# Consolidate by symbol
consolidated_df = consolidate_by_symbol(df)

# Display consolidated data by symbol
print("\nConsolidated Data by Symbol:")
print(consolidated_df)

# Save consolidated data to CSV (if needed)
output_csv = "extracted_data.csv"
consolidated_df.to_csv(output_csv, index=False)
print(f"\nConsolidated data saved to {output_csv}")
