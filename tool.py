# tool.py
# -------------------------------------------------------
# Tool Name : Inventory Stock Flagger
# Domain : Supply Chain / Inventory
# Author : Caleb Schulz
# Description: Processes inventory CSVs to flag empty data (excluding 'NA') 
#              and identify items falling below minimum stock levels. Flagging
#              them and highlighting the cell for a visual representation.
#              This will help companies identify missing data and refill low stock.
# Usage : See README.md for a sample call.
# -------------------------------------------------------
import pandas as pd
import io

def inventory_stock_flagger(csv_content: str) -> dict:
    """
    Scans inventory to flag missing values and stock shortages.
    
    Args:
        csv_content (str): The raw CSV data as a string.
    
    Returns:
        dict: {
            "result": str,
            "unit": "alerts",
            "detail": str,
            "visual_report": str
        }

    Raises:
        ValueError: If required columns 'current_stock' or 'min_stock' are missing.
    """
    # --- Input Validation ---
    try:
        # Loading inventory csv file
        original_df = pd.read_csv(io.StringIO(csv_content), keep_default_na=False)
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")

    # ensures df consistency
    required_cols = ['item_name', 'current_stock', 'min_stock']
    if not all(col in original_df.columns for col in required_cols):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    # --- Core Logic ---

    # Creating a df copy
    working_df = original_df.copy()

    # Marking empty and low stock items
    red_rows = set()
    yellow_rows = set()
    empty_cells = []
    low_stock_items = []

    # Find empty cells (not "NA") and Low Stock
    for index, row in working_df.iterrows():
        # Check for empty cells in any column
        row_num = index + 1
        for col in working_df.columns:
            val = str(row[col]).strip()
            if val == "":
                red_rows.add(index)
                item_label = row.get('item_name', 'Unknown Item')
                empty_cells.append(f"Row {row_num}: {item_label} ({col})")
    
    # Converting to numeric for calculations
    working_df['current_stock'] = pd.to_numeric(working_df['current_stock'], errors='coerce')
    working_df['min_stock'] = pd.to_numeric(working_df['min_stock'], errors='coerce')

    # Check for low stock
    # Skiping "NA"
    for index, row in working_df.iterrows():
        row_num = index + 1
        if pd.notnull(row['current_stock']) and pd.notnull(row['min_stock']):
            if row['current_stock'] < row['min_stock']:
                yellow_rows.add(index)
                low_stock_items.append(f"Row {row_num}: {row['item_name']}")


    # Making Visual Report
    def apply_colors(x):
        # Making df
        style_df = pd.DataFrame('', index=x.index, columns=x.columns)
        
        for idx in x.index:
            # Row has missing data (Red)
            if idx in red_rows:
                style_df.loc[idx, :] = 'background-color: #ffcccc; color: black'
            # Row has low stock (Yellow)
            elif idx in yellow_rows:
                style_df.loc[idx, :] = 'background-color: #fff9c4; color: black'
                        
        return style_df

    styled_html = working_df.style.apply(apply_colors, axis=None).to_html()

    # Change return for main project

    status = "Issues Found" if (empty_cells or low_stock_items) else "Success"

    return {
        "result": status,
        "unit": "alerts",
        "detail": f"Empty cells: {len(empty_cells)}. Low stock: {len(low_stock_items)}.",
        "visual_report": styled_html
    }