import pandas as pd
from typing import List, Dict
import os


def write_to_excel(excel_path: str, data: List[Dict[str, str | float]], sheet_name='Sheet1') -> None:

     # Ensure directory exists
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    try:
        # Try reading the existing excel file
        existing_df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except FileNotFoundError:
        # If the file doesn't exist, start with an empty DataFrame
        existing_df = pd.DataFrame()

    # Create a DataFrame from the new data
    new_data_df = pd.DataFrame(data)

    # Concatenate the existing data with the new data
    updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)

    # Write/overwrite the combined DataFrame to the Excel file
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        updated_df.to_excel(writer, sheet_name=sheet_name, index=False)