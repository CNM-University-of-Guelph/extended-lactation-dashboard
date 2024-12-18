"""Feature construction for multiparous cows."""
import os
import sys

import lmfit
import numpy as np
import pandas as pd
from scipy.stats import linregress
import sklearn.preprocessing
import joblib

from django.conf import settings

pd.options.mode.chained_assignment = None


def multi_feature_construction(
    current_lactation: pd.DataFrame, 
    previous_lactation: pd.DataFrame
) -> pd.DataFrame:
    # 10d milk bins
    features = transform_10d_averages(current_lactation, 60)

    # Cyclic encode month
    min_dim = current_lactation.loc[current_lactation.groupby(["Cow", "Parity"])["DIM"].idxmin()]
    min_dim["month"] = min_dim["Date"].dt.month
    min_dim = min_dim[["Cow", "Parity", "month"]]
    min_dim = cyclic_encode(min_dim, "month", 12)
    features = features.merge(min_dim, on=["Cow", "Parity"], how="left")

    # Fit Dijkstra
    persistency_features = features.apply(
        calculate_previous_persistency, axis=1, args=(previous_lactation,)
        )
    features = pd.concat([features, persistency_features], axis=1)
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    features = features.dropna()

    if features.empty:
        # Error handling is setup in DataUploadView
        return features

    # Previous End of Lactation MY
    features["prev_my_end"] = dijkstra(
        features["prev_lact_length"], features["prev_a"], features["prev_b"],
        features["prev_b0"], features["prev_c"]
    )

    # Previous peak MY
    features["prev_peak_my"] = dijkstra(
        features["prev_days_to_peak"], features["prev_a"], 
        features["prev_b"], features["prev_b0"], 
        features["prev_c"] 
    )

    # Fit Dijkstra (60 DIM + Previous d305 MY)
    current_persistency = features.apply(
        calculate_current_persistency, axis=1, args=(current_lactation,)
        )
    features = pd.concat([features, current_persistency], axis=1) 
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    features = features.dropna()

    if features.empty:
        # Error handling is setup in DataUploadView
        return features

    # Predicted d305 MY
    features["predicted_305_my"] = dijkstra(
        305,
        features["current_a"],
        features["current_b"],
        features["current_b0"],
        features["current_c"]
    )

    # Current days to peak
    features["current_days_to_peak"] = get_dijkstra_days_to_peak(
        features["current_b"], features["current_b0"], 
        features["current_c"]
    )

    # Current peak MY
    features["current_peak_my"] = dijkstra(
        features["current_days_to_peak"],
        features["current_a"],
        features["current_b"],
        features["current_b0"],
        features["current_c"]
    )

    # Predicted persistency
    features["predicted_persistency"] = get_persistency(
        features["predicted_305_my"], features["current_peak_my"], 
        305, features["current_days_to_peak"]
    )

    features["my_variance"] = get_milk_total_variance(current_lactation)
    features["rate_of_my_change"] = get_rate_of_milk_change(current_lactation)

    # Previous Dijkstra parameters adjusted to equation
    features["prev_dijkstra_b_eqn"] = get_dijkstra_b_eqn(
        features["prev_b"]
    )
    features["prev_dijkstra_b0_eqn"] = get_dijkstra_b0_eqn(
        features["prev_b0"], 150
    )
    features["prev_dijkstra_c_eqn"] = get_dijkstra_c_eqn(
        features["prev_c"], 150
    )

    # Current Dijkstra parameters adjusted to equation
    features["current_dijkstra_b_eqn"] = get_dijkstra_b_eqn(
        features["current_b"]
    )
    features["current_dijkstra_b0_eqn"] = get_dijkstra_b0_eqn(
        features["current_b0"], 150
    )
    features["current_dijkstra_c_eqn"] = get_dijkstra_c_eqn(
        features["current_c"], 150
    )

    required_columns = [
        'Parity', 'MilkTotal_1-10', 'MilkTotal_11-20', 'MilkTotal_21-30', 
        'MilkTotal_31-40', 'MilkTotal_41-50', 'MilkTotal_51-60', 'month_sin', 
        'month_cos', 'prev_a', 'prev_305_my', 'prev_lact_length', 'prev_my_end', 
        'prev_days_to_peak', 'prev_peak_my', 'prev_persistency', 'current_a', 
        'predicted_305_my', 'current_days_to_peak', 'current_peak_my', 
        'predicted_persistency', 'my_variance', 'rate_of_my_change', 
        'prev_dijkstra_b_eqn', 'prev_dijkstra_b0_eqn', 'prev_dijkstra_c_eqn', 
        'current_dijkstra_b_eqn', 'current_dijkstra_b0_eqn', 'current_dijkstra_c_eqn'
    ]

    # Ensure only the required columns are included and in the specified order
    features = features[required_columns]

    # MinMax Scaling
    scalers_dir = os.path.join(settings.BASE_DIR, "api/scalers")
    scaler_path = os.path.join(scalers_dir, "multiparous_scaler.joblib")
    scaler = joblib.load(scaler_path)
    scaled_data = scaler.transform(features)
    scaled_data = pd.DataFrame(scaled_data, columns=required_columns)
    return scaled_data


def transform_10d_averages(df: pd.DataFrame, dim: int) -> pd.DataFrame:
    """
    Transform data from long to wide format, averging into 10 day bins

    Names are currently hard coded, funciton should be modified to take column
    names as arguments
    """
    # Isolate DIM 305 data for the MilkTotal values
    # dim_305_data = df[df['DIM'] == 305][['Cow', 'Parity', 'MilkTotal']]
    # dim_305_data.rename(columns={'MilkTotal': 'MilkTotal_305'}, inplace=True)
    daily_data_1_to_dim = df[df['DIM'] <= dim]

    # Define 10-day bins for the DIM from 1 to 60
    bins_1_to_dim = np.arange(0, (dim + 1), 10)
    labels_1_to_dim = [f'{i+1}-{i+10}' for i in range(0, dim, 10)]
    daily_data_1_to_dim['DIM_bin'] = pd.cut(daily_data_1_to_dim['DIM'], bins=bins_1_to_dim, labels=labels_1_to_dim, right=False)
    grouped_data_1_to_dim = daily_data_1_to_dim.groupby(['Cow', 'Parity', 'DIM_bin'], observed=False).agg({
        'MilkTotal': 'mean',
    }).reset_index()

    # Pivot the data to a wide format
    pivot_data_1_to_dim = grouped_data_1_to_dim.pivot_table(index=['Cow', 'Parity'], 
                                                            observed=False,
                                                            columns='DIM_bin',
                                                            values=['MilkTotal']
                                                        )
    pivot_data_1_to_dim.columns = ['{}_{}'.format(col[0], col[1]) for col in pivot_data_1_to_dim.columns]
    pivot_data_1_to_dim.reset_index(inplace=True)
    # final_data = pd.merge(pivot_data_1_to_dim, dim_305_data, on=['Cow', 'Parity'], how='left')
    return pivot_data_1_to_dim


def cyclic_encode(df: pd.DataFrame, col_name: str, n: int) -> pd.DataFrame:
    column = df.pop(col_name)
    df[f"{col_name}_sin"] = np.sin(2 * np.pi * column / n) 
    df[f"{col_name}_cos"] = np.cos(2 * np.pi * column / n) 
    return df


def calculate_previous_persistency(row, previous_lactation):
    cow = row['Cow']
    parity = row['Parity'] - 1

    data = previous_lactation[(previous_lactation['Cow'] == cow) &
                             (previous_lactation['Parity'] == parity)]
    if data.empty or len(data) <= 60:
        return pd.Series({
                          'prev_persistency': np.nan, 
                          "prev_lact_length": np.nan, 
                          "prev_days_to_peak": np.nan, 
                          "prev_305_my": np.nan
                          })

    x = data['MilkTotal']
    t = data['DIM']
    param_specs = {
        'a': {'value': 30, 'min': 0, 'max': 100},
        'b': {'value': 0.01, 'min': 0.0001, 'max': 0.09},
        'b0': {'value': 0.01, 'min': 0, 'max': 0.09},
        'c': {'value': 0.001, 'min': 0, 'max': 0.005}
        }
    dijkstra_fit = fit_model(dijkstra, param_specs, x, t)
    a = dijkstra_fit['a']
    b = dijkstra_fit['b']
    b0 = dijkstra_fit['b0']
    c = dijkstra_fit['c']

    t_end = data['DIM'].max()
    my_end = dijkstra(t_end, a, b, b0, c)
    pt = round(np.log(b / c) / b0)
    py = dijkstra(pt, a, b, b0, c)

    prev_305_my = calculate_previous_305_my(row, previous_lactation)

    persistency = calculate_persistency(my_end, py, t_end, pt)
    return pd.Series({
        'prev_a': a,
        'prev_b': b,
        'prev_b0': b0,
        'prev_c': c,
        'prev_persistency': persistency, 
        'prev_lact_length': t_end,
        'prev_days_to_peak': pt,
        "prev_305_my": prev_305_my}
        )


def dijkstra(t, a, b, b0, c):
    return a * np.exp((b * (1 - np.exp(-b0 * t)) / b0) - c * t)


def fit_model(func, param_specs, x, t):
    model = lmfit.Model(func)
    params = model.make_params()
    for param_name, specs in param_specs.items():
        if 'min' in specs and 'max' in specs:
            params[param_name].set(value=specs['value'], min=specs['min'], max=specs['max'])
        else:
            params[param_name].set(value=specs['value'])

    result = model.fit(x, params, t=t, method='leastsq')
    best_fit_params = result.params.valuesdict()
    return best_fit_params


def calculate_previous_305_my(row, previous_lactation):
    cow = row['Cow']
    parity = row['Parity'] - 1  

    if parity > 0:
        filtered = previous_lactation[(previous_lactation['Cow'] == cow) &
                                      (previous_lactation['Parity'] == parity) &
                                      (previous_lactation['DIM'].between(303, 307))]
        if not filtered.empty:
            return filtered['MilkTotal'].mean()

        elif filtered.empty:
            # Handle cases where there is no DIM 303-307 records for the previous lactation
            cow_prev_lac = previous_lactation[(previous_lactation['Cow'] == cow) &
                                            (previous_lactation['Parity'] == parity) &
                                            (previous_lactation['DIM'] < 305)]
            closest_dim = cow_prev_lac["DIM"].max()
            closest_records = previous_lactation[(previous_lactation['Cow'] == cow) &
                                                (previous_lactation['Parity'] == parity) &
                                                (previous_lactation['DIM'].between(closest_dim - 5, closest_dim))]
            if not closest_records.empty:
                return closest_records["MilkTotal"].mean()

    return np.nan  


def calculate_persistency(my_end, py, t_end, pt):
    """
    my_end (float): milk yield end of lactation
    py (float): peak milk yield
    t_end (float): days to end of lactation
    pt (float): days to peak milk yield
    """
    return (my_end - py) / (t_end - pt)


def calculate_current_persistency(row, current_lactation):
    cow = row["Cow"]
    parity = row["Parity"]    
    data = current_lactation[(current_lactation["Cow"] == cow) &
                             (current_lactation["Parity"] == parity) & 
                             (current_lactation["DIM"] <= 60)]
    
    if data.empty or len(data) < 50:
        print(f"Cow: {cow} Parity: {parity} had < 50 DIM for current lactation. {len(data)}")
        return pd.Series({'persistency': np.nan,
                          "days_to_peak": np.nan, 
                          "predicted_305_my": np.nan,
                        #   "a": np.nan,
                        #   "b": np.nan,
                        #   "b0": np.nan,
                        #   "c": np.nan
                          }
                          )

    x = data['MilkTotal']
    x = pd.concat([x, pd.Series([row['prev_305_my']])], ignore_index=True)

    t = data['DIM']
    t = pd.concat([t, pd.Series([305])], ignore_index=True)

    param_specs = {
        'a': {'value': 30, 'min': 0, 'max': 100},
        'b': {'value': 0.01, 'min': 0.0001, 'max': 0.09},
        'b0': {'value': 0.01, 'min': 0, 'max': 0.09},
        'c': {'value': 0.001, 'min': 0, 'max': 0.005}
        }
    
    dijkstra_fit = fit_model(dijkstra, param_specs, x, t)
    a = dijkstra_fit['a']
    b = dijkstra_fit['b']
    b0 = dijkstra_fit['b0']
    c = dijkstra_fit['c']

    t_end = 305
    my_end = dijkstra(t_end, a, b, b0, c)
    pt = round(np.log(b / c) / b0)
    py = dijkstra(pt, a, b, b0, c)

    persistency = calculate_persistency(my_end, py, t_end, pt)
    return pd.Series({
        "persistency": persistency,
        "days_to_peak": pt,
        "predicted_305_my": my_end,
        "current_a": a,
        "current_b": b,
        "current_b0": b0,
        "current_c": c
    })


def get_persistency(my_end, py, t_end, pt):
    """
    my_end (float): milk yield end of lactation
    py (float): peak milk yield
    t_end (float): days to end of lactation
    pt (float): days to peak milk yield
    """
    return (my_end - py) / (t_end - pt)


def get_dijkstra_days_to_peak(b, b0, c):
    return round(np.log(b / c) / b0) 


def get_milk_total_variance(current_lactation):
    """
    Calculate the variance of MilkTotal over the first 60 DIM using data_import
    and add it to transformed_data as the column 'my_variance'.
    """
    variance_data = current_lactation[current_lactation['DIM'] <= 60]['MilkTotal'].copy()
    my_variance = variance_data.var()
    return my_variance


def get_rate_of_milk_change(current_lactation):
    """
    Fit a line to MilkTotal over the first 60 DIM using data_import, 
    calculate the slope, and add it to transformed_data as 'rate_of_my_change'.
    """
    change_data = current_lactation[current_lactation['DIM'] <= 60].copy()
    
    if len(change_data) > 1:
        slope, _, _, _, _ = linregress(change_data['DIM'], change_data['MilkTotal'])
    else:
        slope = np.nan 
    
    return slope


def get_dijkstra_b_eqn(b):
    return np.exp(b)


def get_dijkstra_b0_eqn(b0, t):
    return np.exp(-b0 * t)


def get_dijkstra_c_eqn(c, t):
    return np.exp(-c * t)
