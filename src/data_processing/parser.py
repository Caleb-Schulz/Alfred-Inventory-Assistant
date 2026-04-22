# parser.py
import pandas as pd
from cleaner import standardize_column_names, clean_missing_values

# Reads the inventory csv file and returns it as a dataframe
def read_inventory_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = standardize_column_names(df)
    df = clean_missing_values(df)
    return df

# tests the parser with a sample csv
if __name__ == "__main__":
    df = read_inventory_csv("data/sample_inventory_messy.csv")
    print(df.head())
    print(df.columns)