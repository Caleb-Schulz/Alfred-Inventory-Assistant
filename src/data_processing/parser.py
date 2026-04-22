# parser.py
import pandas as pd
from cleaner import standardize_column_names, clean_missing_values, normalize_text_fields
from validator import validate_required_columns, validate_numeric_columns, flag_negative_values

# Reads the inventory csv file and returns it as a dataframe
def read_inventory_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = standardize_column_names(df)
    validate_required_columns(df)
    df = clean_missing_values(df)
    df = normalize_text_fields(df)
    validate_numeric_columns(df)
    df = flag_negative_values(df)
    return df

# tests the parser with a sample csv
if __name__ == "__main__":
    df = read_inventory_csv("data/sample_inventory_messy.csv")
    print(df.head())
    print(df.columns)