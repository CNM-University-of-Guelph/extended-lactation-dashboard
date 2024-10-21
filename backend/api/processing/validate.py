"""Validate the uploaded data has all the required data."""

import pandas as pd

def validate(df: pd.DataFrame) -> pd.DataFrame:
    messages = []

    try:
        column_check = validate_and_clean_columns(df, messages)
    except ValueError as e:
        messages.append(str(e))
        raise e
    
    column_check["Date"] = pd.to_datetime(
        column_check["Date"], format="%Y-%m-%d", errors="coerce"
        )

    if column_check["Date"].isnull().any():
        invalid_dates = column_check[column_check["Date"].isnull()]
        messages.append(f"Invalid dates found in rows: {invalid_dates.index.tolist()}")
        raise ValueError(
            "Date column contains invalid dates that could not be converted."
            )
    
    eligible_lactations, ineligible_lactations = get_eligible_lactations(column_check)
    
    if ineligible_lactations:
        messages.append(format_ineligible_lactations(ineligible_lactations))

    return column_check, eligible_lactations, messages


def validate_and_clean_columns(df: pd.DataFrame, messages: list) -> pd.DataFrame:
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
        error_message = f"Missing required columns: {', '.join(missing_columns)}"
        messages.append(error_message)
        raise ValueError(error_message)

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
    ineligible_pairs = []

    grouped = df.groupby(['Cow', 'Parity'])

    for (cow, parity), group in grouped:       
        # Condition 1: At least 50 records between 0 and 60 DIM
        if len(group[(group['DIM'] >= 0) & (group['DIM'] <= 60)]) < 50:
            ineligible_pairs.append((cow, parity, "Less than 50 records between 0 and 60 DIM"))
            continue
        
        # Condition 2: Check the previous parity exists (Multiparous)
        if parity > 1:
            previous_parity_group = df[(df['Cow'] == cow) & (df['Parity'] == parity - 1)]
            if len(previous_parity_group) < 100:
                ineligible_pairs.append((cow, parity, "Less than 100 records for previous parity"))
                continue

        eligible_pairs.append((cow, parity))
    
    return eligible_pairs, ineligible_pairs


def format_ineligible_lactations(ineligible_pairs):
    """Format ineligible lactations as a multi-line string."""
    if not ineligible_pairs:
        return "No ineligible lactations found."

    formatted_message = "Ineligible lactations:\n"
    formatted_message += "\n".join([f"- Cow: {cow}, Parity: {parity}, Reason: {reason}" 
                                    for cow, parity, reason in ineligible_pairs])
    return formatted_message
