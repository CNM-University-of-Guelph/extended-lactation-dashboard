"""Validate the uploaded data has all the required data."""

import pandas as pd

def validate(df: pd.DataFrame) -> pd.DataFrame:
    column_check = validate_and_clean_columns(df)
    column_check["Date"] = pd.to_datetime(
        column_check["Date"], format="%Y-%m-%d", errors="coerce"
        )
    
    # TODO Once I have a better idea of what the uplaoded dataset will look like
    # this module should be enhanced. It should check that we have the current 
    # and previous lactation. It should aslo check we have the dam's first 
    # lactation for primiparous cows

    # NOTE Should primiparous and multiparous be uploaded as seperate files?

    if column_check["Date"].isnull().any():
        raise ValueError(
            "Date column contains invalid dates that could not be converted."
            )
    return column_check


def validate_and_clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates that the DataFrame contains only the specified columns 
    and removes any additional columns.
    
    Args:
        df (pd.DataFrame): The input DataFrame to validate.
    
    Returns:
        pd.DataFrame: A cleaned DataFrame containing only the required columns.
    
    Raises:
        ValueError: If any of the required columns are missing.
    """
    required_columns = ['Cow', 'DIM', 'Parity', 'Date', 'MilkTotal']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    df_cleaned = df[required_columns].copy()
    
    return df_cleaned
