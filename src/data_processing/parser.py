import pandas as pd
from cleaner import standardize_column_names

def read_inventory_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = standardize_column_names(df)
    return df

if __name__ == "__main__":
    df = read_inventory_csv("data/sample_inventory_messy.csv")
    print(df.head())
    print(df.columns)