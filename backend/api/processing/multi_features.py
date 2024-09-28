"""Feature construction for multiparous cows."""
import os
import sys

import lmfit
import numpy as np
import pandas as pd
import sklearn.preprocessing

def multi_feature_construction(
    current_lactation: pd.DataFrame, 
    previous_lactation: pd.DataFrame
) -> pd.DataFrame:
    # 10d milk bins
    features = transform_10d_averages(current_lactation, 60)

    # Cyclic encode month
    min_dim = current_lactation.loc[current_lactation.groupby(["Cow", "Parity"])["DIM"].idxmin()]
    min_dim["Month"] = min_dim["Date"].dt.month
    min_dim = min_dim[["Cow", "Parity", "Month"]]
    min_dim = cyclic_encode(min_dim, "Month", 12)
    features = features.merge(min_dim, on=["Cow", "Parity"], how="left")

    # Fit Dijkstra
    persistency_features = features.apply(
        calculate_previous_persistency, axis=1, args=(previous_lactation,)
        )
    features = pd.concat([features, persistency_features], axis=1)
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    features = features.dropna()

    # Fit Dijkstra (60 DIM + Previous d305 MY)
    current_persistency = features.apply(
        calculate_current_persistency, axis=1, args=(current_lactation,)
        )
    features = pd.concat([features, current_persistency], axis=1) 
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    features = features.dropna()

    # MinMax Scaling # TODO activate after testing the pipeline is working properly
    features = features.drop(columns={"Cow"})
    # cow_id = features.pop("Cow")
    # month_cos = features.pop("Month_cos")
    # month_sin = features.pop("Month_sin")

    # scaler = sklearn.preprocessing.MinMaxScaler(feature_range=(-1, 1))
    # scaled_data = scaler.fit_transform(features)
    # scaled_dataset = pd.DataFrame(scaled_data, columns=features.columns)
    # scaled_dataset.insert(0, "Cow", cow_id.values)
    # scaled_dataset["Month_sin"] = month_sin.values
    # scaled_dataset["Month_cos"] = month_cos.values

    return features


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
    grouped_data_1_to_dim = daily_data_1_to_dim.groupby(['Cow', 'Parity', 'DIM_bin']).agg({
        'MilkTotal': 'mean',
    }).reset_index()

    # Pivot the data to a wide format
    pivot_data_1_to_dim = grouped_data_1_to_dim.pivot_table(index=['Cow', 'Parity'],
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
                          "prev_lactation_length": np.nan, 
                          "prev_days_to_peak": np.nan, 
                          "prev_305_my": np.nan
                          })

    x = data['MilkTotal']
    t = data['DIM']
    param_specs = {
        'a': {'value': 100, 'min': 0, 'max': 250},
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
        'prev_persistency': persistency, 
        'prev_lactation_length': t_end,
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
        'a': {'value': 100, 'min': 0, 'max': 250},
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
        # "a": a,
        # "b": b,
        # "b0": b0,
        # "c": c
    })
