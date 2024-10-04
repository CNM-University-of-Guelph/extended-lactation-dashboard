"""Validate the uploaded data has all the required data."""

import pandas as pd

def validate(df: pd.DataFrame) -> pd.DataFrame:
    column_check = validate_and_clean_columns(df)
    column_check["Date"] = pd.to_datetime(
        column_check["Date"], format="%Y-%m-%d", errors="coerce"
        )
    eligible_lactations = get_eligible_lactations(column_check)
    
    # TODO Once I have a better idea of what the uplaoded dataset will look like
    # this module should be enhanced. It should check that we have the current 
    # and previous lactation. It should aslo check we have the dam's first 
    # lactation for primiparous cows

    if column_check["Date"].isnull().any():
        raise ValueError(
            "Date column contains invalid dates that could not be converted."
            )
    return column_check, eligible_lactations


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


def get_eligible_lactations(df: pd.DataFrame) -> list:
    """Generates a list of Cow-Parity pairs eligible for ML based on the conditions.
    
    Args:
        df (pd.DataFrame): The validated DataFrame.
        
    Returns:
        eligible_pairs (list): A list of tuples (Cow, Parity) eligible for ML.
    """
    eligible_pairs = []

    grouped = df.groupby(['Cow', 'Parity'])

    for (cow, parity), group in grouped:
        # Condition 1: Multiparous lactation
        if parity == 1:
            continue
        
        # Condition 2: At least 50 records between 0 and 60 DIM
        if len(group[(group['DIM'] >= 0) & (group['DIM'] <= 60)]) < 50:
            continue
        
        # Condition 3: Check the previous parity (Parity - 1)
        previous_parity_group = df[(df['Cow'] == cow) & (df['Parity'] == parity - 1)]
        if len(previous_parity_group) < 100:
            continue

        eligible_pairs.append((cow, parity))
    
    return eligible_pairs
