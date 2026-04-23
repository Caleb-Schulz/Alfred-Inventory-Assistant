#Making a tool that would allow the agent to add any data to any column
import pandas as pd
from Langchain.tools import tool 
@tool("add_data_to_column", return_direct=True)

def add_data_to_column(df: pd.DataFrame, column_name: str, data) -> pd.DataFrame:
    """
    Add data to a specific column in the DataFrame.
    Args:
        df (pd:DataFrame): The input DataFrame.
        column_name(str): The name of the column to which data should be added.
        data: The data to be added to the column. This can be a single value or a list of values.
        Returns:
        pd.DataFrame: The updated DataFrame with the new data added to the specified column.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
    if isinstance(data, list):
        if len(data) != len(df):
            raise ValueError("Length of the data list must match the number of rows in the DataFrame.")
        df[column_name] = data
    else:
        df[column_name] = data
    return df


    



        