import pandas as pd

# exports the cleaned dataframe to a new csv file
def export_clean_inventory_csv(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False)