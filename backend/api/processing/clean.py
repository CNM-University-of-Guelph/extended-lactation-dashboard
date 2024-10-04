"""Clean the raw data, fixing DIM, parity and milk yield outliers."""
import os
from typing import Union

import numpy as np
import pandas as pd
import statsmodels.api as sm


def clean(df: pd.DataFrame) -> pd.DataFrame:
    data_grouped = df.groupby(by=["Cow", "Parity"])
    print(f"Number of unique lacations: {data_grouped.ngroups}")

    # Correct parity
    parity_corrected_data = parity_correction(df)
    
    # Correct DIM
    cow_parity_groups = parity_corrected_data.groupby(by=["Cow", "Parity"])
    corrected_DIM = (cow_parity_groups
                    .apply(correct_dim, include_groups=False)
                    .reset_index(level=[0, 1])
                    .drop(columns='DIM')
                    .rename(columns={'corrected_DIM': 'DIM'})
                    )
    
    # Outlier Removal (LOESS)
    lactations = corrected_DIM.groupby(by=["Cow", "Parity"])
    lactations_smoothed = lactations.apply(
        lambda group: smooth_impute_plot(
            group,
            y_column="MilkTotal",
            smoothed_column="SmoothedMilkTotal",
            frac=0.1,
            output_folder="./milk_loess"
        ), include_groups=False
    ).reset_index(level=[0, 1])

    lactations_smoothed_outliers = detect_outliers(lactations_smoothed,
                                                    "SmoothedMilkTotal",
                                                    "MilkTotal",
                                                    "my_residual",
                                                    group_criteria=["Cow", "Parity"]) 
    outlier_mask = lactations_smoothed_outliers['is_outlier']
    lactations_smoothed_outliers.loc[outlier_mask, 'MilkTotal'] = lactations_smoothed_outliers.loc[outlier_mask, 'SmoothedMilkTotal']
    columns_to_drop = ['my_residual', 'residual_sd', 'SD_ratio', 'SD_from_fitted', 'is_outlier', 'SmoothedMilkTotal']
    lactations_smoothed = lactations_smoothed_outliers.drop(columns=columns_to_drop)
         
    return lactations_smoothed


def find_gaps_and_calving_dates(
    group: pd.DataFrame, 
    date_col: str = "Date"
) -> list:
    """
    Identifies potential calving dates in a DataFrame by examining gaps in 
    milking data. It calculates the days between consecutive milking records and
    considers a gap of 15 or more days as an indicator of a new calving event. 
    The function returns these dates sorted in chronological order.


    Args:
        group (pd.DataFrame): The data for one cow to check, must have a date column
        date_col (str): The name of the date column. Default is "Date"

    Returns:
        list of datetime.date: A list of dates sorted in chronological order that potentially indicate new calving events.
    """
    df = group.copy()
    df["days_since_last_milking"] = df[date_col].diff().dt.days
    filtered_rows = df[df["days_since_last_milking"] >= 15]
    new_calving_dates = filtered_rows[date_col].dt.strftime("%Y-%m-%d")
    return pd.to_datetime(new_calving_dates).sort_values().to_list()


def filter_dataframe_by_dates(
    group: pd.DataFrame, 
    list_of_dates: list,
    date_col: str = "Date"
) -> dict:
    """
    This function creates intervals based on a list of dates to partition the 
    DataFrame. Each resulting subset contains data falling into one of these 
    intervals: before the first date, between consecutive dates, and after the 
    last date.

    Args:
        group (pd.DataFrame): The data for one cow, must contain date column
        list_of_dates (list): A list of dates that define the boundaries for filtering the DataFrame. 
        date_col
        
    Returns:
        dict of pd.DataFrame: A dictionary where each key corresponds to a subset and its value is a DataFrame for that interval.
    """
    if not list_of_dates:
        return {"lactation": group}

    list_of_dates = pd.to_datetime(list_of_dates)
    list_of_dates = sorted(list_of_dates)
    # Initialize mask with before the first date
    masks = [(group[date_col] < list_of_dates[0])]
    # Update masks for between dates if there is more than one date
    if len(list_of_dates) > 1:
        masks.extend(((group[date_col] >= list_of_dates[i]) & 
                      (group[date_col] < list_of_dates[i + 1])).tolist() 
                      for i in range(len(list_of_dates) - 1)
                      )
    # Update masks for after the last date
    masks.append((group[date_col] >= list_of_dates[-1]).tolist())
    result_dict = {}
    for i, mask in enumerate(masks):
        result_dict[f"lactation_{i + 1}"] = group[mask]
    return result_dict


def correct_lact_n(filtered_lactations: dict, 
                   dim_col: str = "DIM",
                   parity_col: str = "Parity"
) -> dict:
    """
    Corrects the parity numbers for each subset of lactations in a dictionary of dataframes based on
    Days in Milk (DIM) criteria. It applies corrections by assigning the most frequent parity number observed
    within the valid DIM range (10 to 300 days) to all entries in the subset. If no entries fall within this range,
    the function uses the last corrected parity or increments it if it was the last in sequence.

    Args:
        filtered_lactations (dict of pd.DataFrame): A dictionary where each key is a subset identifier and each value is
        a dataframe containing lactation records, including 'DIM' and 'Parity' columns.

    Returns:
        dict of pd.DataFrame: The modified dictionary with corrected parity numbers in each dataframe.
    """
    last_corrected_lact_n = None

    for key, subset in filtered_lactations.items():
        df = subset.copy()
        if df.empty:
            continue

        relevant_rows = df[(df[dim_col] > 10) & (df[dim_col] < 300)]
        
        if not relevant_rows.empty:
            mode_lact_n = relevant_rows[parity_col].mode().iloc[0]
            last_corrected_lact_n = mode_lact_n
            df['Corrected_Parity'] = mode_lact_n
        else:
            if last_corrected_lact_n is not None:
                df['Corrected_Parity'] = last_corrected_lact_n + 1
            else:
                df['Corrected_Parity'] = df[parity_col]

        filtered_lactations[key] = df
    return filtered_lactations


def parity_correction(df: pd.DataFrame) -> pd.DataFrame:
    cow_groups = df.sort_values(by=["Cow", "Date"]).groupby("Cow")
    parity_corrected_groups = []

    for cow_id, group in cow_groups:
        lactation_gaps = find_gaps_and_calving_dates(group)
        filtered_lactations = filter_dataframe_by_dates(
            group, lactation_gaps
            )
        corrected_lactations = correct_lact_n(filtered_lactations)
        corrected_group = pd.concat(corrected_lactations.values(),
                                    ignore_index=True)
        parity_corrected_groups.append(corrected_group)

    parity_corrected_data = pd.concat(parity_corrected_groups,
                                    ignore_index=True
                                    ).drop(columns="Parity").rename(columns={"Corrected_Parity": "Parity"})
    return parity_corrected_data


def correct_dim(
    group: pd.DataFrame, 
    date_col: str = "Date", 
    dim_col: str = "DIM"
) -> pd.DataFrame:
    """
    Sorts and corrects the 'DIM' (Days in Milk) values within a dataframe grouped by lactation based on the Date column.

    Args:
        group (pd.DataFrame): Data for a single lactation

    Returns:
        pd.DataFrame: The dataframe with corrected 'DIM' values.
    """
    sorted_group = group.sort_values(by=date_col)
    
    if sorted_group[dim_col].isna().all():
        # Assume the first date has 'DIM' equal to 0 if no DIM values for group
        sorted_group["corrected_DIM"] = sorted_group[date_col].diff().dt.days.fillna(0).cumsum()
    else:
        # Find the middle row where 'DIM' is not NaN. Mistakes most frequently occur at start and end of lactations
        middle_row = sorted_group.loc[~sorted_group[dim_col].isna()].iloc[len(sorted_group) // 2]
        if not pd.isna(middle_row[dim_col]):
            sorted_group["corrected_DIM"] = (
                middle_row[dim_col] + 
                (sorted_group[date_col] - middle_row[date_col]).dt.days)  
            if (sorted_group["corrected_DIM"] < 0).sum() > 3:
                sorted_group["corrected_DIM"] = sorted_group[dim_col]
        else:
            sorted_group["corrected_DIM"] = sorted_group[dim_col]
    return sorted_group


def smooth_impute_plot(group: pd.DataFrame,
                       y_column: str, 
                       smoothed_column: str,
                       dim_column: str = "DIM", 
                       frac: float = 0.10,
                       output_folder: str = './plots',
) -> pd.DataFrame:
    """
    Applies LOWESS smoothing to non-missing values of a specified column in a DataFrame group, imputes missing values
    using the smoothed results, and plots the original versus smoothed data. The plot is saved in a specified directory.

    Args:
        group (pd.DataFrame): The DataFrame group to be smoothed and imputed. Must include 'DIM' as a column.
        y_column (str): The name of the column containing the original data, which may include NaNs that need imputation.
        smoothed_column (str): The name of the column where smoothed data will be stored.
        dim_column (str): Name of the days in milk column
        frac (float, optional): The fraction of the data used when estimating each y-value in the LOWESS. Defaults to 0.10.
        output_folder (str, optional): The root directory where the plots will be saved. Defaults to './plots'.
        
    Returns:
        pd.DataFrame: The DataFrame group with smoothed and imputed values added.
    """
    x = group[dim_column].values
    y = group[y_column].values

    nan_indices = np.isnan(y)

    if sum(~nan_indices) > 1: 
        lowess_result = sm.nonparametric.lowess(y[~nan_indices], x[~nan_indices], frac=frac)
        smoothed_values = lowess_result[:, 1]
        smoothed_values_rounded = np.round(smoothed_values, 1)
        group.loc[:, smoothed_column] = np.interp(x, x[~nan_indices], smoothed_values_rounded)
        group.loc[nan_indices, y_column] = group.loc[nan_indices, smoothed_column]
    else:
        group.loc[:, smoothed_column] = y
    
    return group


def detect_outliers(df: pd.DataFrame, 
                    smoothed_column: str, 
                    original_column: str, 
                    residual_column: str,
                    group_criteria: list = ["Cow", "Parity"]
) -> pd.DataFrame:
    """
    Calculates residuals from smoothed and original data columns in a DataFrame, computes the standard deviation of
    these residuals grouped by 'Cow' and 'Parity', and classifies each data point as an outlier if the residual exceeds
    three standard deviations.

    Previously named smooth_residuals

    Args:
        df (pd.DataFrame): The DataFrame containing the original and smoothed data.
        smoothed_column (str): The column name containing the smoothed data.
        original_column (str): The column name containing the original data to compare against the smoothed data.
        residual_column (str): The column name where the calculated residuals will be stored.
        group_criteria (list): Names of columns to use for grouping
        
    Returns:
        pd.DataFrame: A DataFrame with additional columns for residual standard deviation, standard deviation ratio, residual
        category (binned by standard deviation ratio), and an outlier flag.
    """
    df_smoothed_residual = df.copy()
    df_smoothed_residual[residual_column] = df_smoothed_residual[smoothed_column] - df_smoothed_residual[original_column]
    df_smoothed_residual["residual_sd"] = (
        df_smoothed_residual.groupby(by=group_criteria)[residual_column]
        .transform("std")
    )
    df_smoothed_residual["SD_ratio"] = (
        abs(df_smoothed_residual[residual_column]) / df_smoothed_residual["residual_sd"]
    )
    df_smoothed_residual["SD_from_fitted"] = (
        pd.cut(
            df_smoothed_residual["SD_ratio"],
            bins=10,
            include_lowest=True,
            labels=False 
        ).astype(float)     
    )
    df_smoothed_residual["SD_from_fitted"] = df_smoothed_residual["SD_from_fitted"].fillna(0)
    df_smoothed_residual["is_outlier"] = (
        (abs(df_smoothed_residual[residual_column]) >= (df_smoothed_residual["residual_sd"] * 3)) &
        (df_smoothed_residual[residual_column] != 0)
    )
    return df_smoothed_residual


def filter_dim_lactation(group: pd.DataFrame, 
                         dim: int,
                         dim_col: str = "DIM"
) -> Union[pd.DataFrame, None]:
    """
    Filters a DataFrame group to return records from the specified range (1-dim days) and late (303-307 days) lactation periods.
    The function checks if there are any records within these specified periods and returns the filtered data if both periods
    have data. If either period lacks data, it returns None.

    Args:
        group (pd.DataFrame): The DataFrame containing lactation data, expected to have a 'DIM' column.
        dim (int): max DIM to include in dataset

    Returns:
        pd.DataFrame or None: A DataFrame containing only the records from the specified early and late lactation periods,
        or None if one or both periods do not have any records.
    """
    has_data_0_dim = any((group[dim_col] >= 1) & (group[dim_col] <= dim))
    has_data_303_307 = any((group[dim_col] >= 303) & (group[dim_col] <= 307))

    if has_data_0_dim and has_data_303_307:
        condition = (((group[dim_col] >= 1) & 
                      (group[dim_col] <= dim)) | 
                     ((group[dim_col] >= 303) & 
                      (group[dim_col] <= 307)))
        return group[condition]
    else:
        return None
