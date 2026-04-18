Inventory Stock Flagger
You will upload your inventory CSV file to the tool, and it will flag any missing data or items with low stock in both text and visual form.

Installation:
pip install pandas pytest

Usage Example:
from tool import inventory_stock_flagger

# Example CSV input
csv_data = """item_name,current_stock,min_stock
Widget_A,5,10
Widget_B,,50
Widget_C,NA,5"""

# Execute the tool
response = inventory_stock_flagger(csv_data)

print(f"Status: {response['result']}")
print(f"Details: {response['detail']}")
# response['visual_report'] contains the HTML for a styled table

SNAP Project Integration:
This is just one of the many tools we will include in our project. Our LLM will review the flagged data, notify you, and assist you with it.