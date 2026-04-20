import pandas as pd

def read_inventory_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

if __name__ == "__main__":
    df = read_inventory_csv("data/sample_inventory_messy.csv")
    print(df.head())