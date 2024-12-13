"""Feature construction for primiparous cows."""

import numpy as np
import pandas as pd
import os
import lmfit
import joblib
from scipy.stats import linregress

from django.conf import settings


from .feature_construction_helpers import transform_10d_averages, cyclic_encode

pd.options.mode.chained_assignment = None

def primi_feature_construction(current_lactation):
    #10d milk bins
    features = transform_10d_averages(current_lactation, 60)

    # Cyclic encode month
    min_dim = current_lactation.loc[current_lactation.groupby(["Cow"])["DIM"].idxmin()]
    min_dim["month"] = min_dim["Date"].dt.month
    min_dim = min_dim[["Cow", "month"]]
    min_dim = cyclic_encode(min_dim, "month", 12)
    features = features.merge(min_dim, on=["Cow"], how="left")

    # Fit Dijkstra (60 DIM + Previous d305 MY)
    current_persistency = features.apply(
        get_dijkstra_params, axis=1, args=(current_lactation,)
        )
    features = pd.concat([features, current_persistency], axis=1) 
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    features = features.dropna()
    if features.empty:
        # Error handling is setup in DataUploadView
        return features

    features["my_variance"] = get_milk_total_variance(current_lactation)
    features["rate_of_my_change"] = get_rate_of_milk_change(current_lactation)

    # Current Dijkstra parameters adjusted to equation
    features["current_dijkstra_b_eqn"] = get_dijkstra_b_eqn(
        features["b"]
    )
    features["current_dijkstra_b_b0_eqn"] = get_dijkstra_b_b0_eqn(
        features["b"], features["b0"], 150
    )
    features["current_dijkstra_b0_eqn"] = get_dijkstra_b0_eqn(
        features["b0"], 150
    )
    features["current_dijkstra_c_eqn"] = get_dijkstra_c_eqn(
        features["c"], 150
    )

    required_columns = [
        'MilkTotal_1-10', 'MilkTotal_11-20', 'MilkTotal_21-30', 
        'MilkTotal_31-40', 'MilkTotal_41-50', 'MilkTotal_51-60', 'month_sin', 
        'month_cos', 'a', "my_variance", "rate_of_my_change", "predicted_305_my",
        "current_dijkstra_b_eqn", "current_dijkstra_b_b0_eqn", "current_dijkstra_b0_eqn",
        "current_dijkstra_c_eqn"
    ]
    features = features[required_columns]

    # MinMax Scaling
    scalers_dir = os.path.join(settings.BASE_DIR, "api/scalers")
    scaler_path = os.path.join(scalers_dir, "primiparous_scaler.joblib")
    scaler = joblib.load(scaler_path)
    scaled_data = scaler.transform(features)
    scaled_data = pd.DataFrame(scaled_data, columns=required_columns)
    return scaled_data



def dijkstra(t, a, b, b0, c):
    return a * np.exp((b * (1 - np.exp(-b0 * t)) / b0) - c * t)


def get_dijkstra_params(row, current_lactation):
    cow = row["Cow"]
    parity = row["Parity"]    
    data = current_lactation[(current_lactation["Cow"] == cow) &
                             (current_lactation["Parity"] == parity) & 
                             (current_lactation["DIM"] <= 60)]
    
    if data.empty or len(data) < 50:
        print(f"Cow: {cow} Parity: {parity} had < 50 DIM for current lactation. {len(data)}")
        return pd.Series({"predicted_305_my": np.nan,
                          "a": np.nan,
                          "b": np.nan,
                          "b0": np.nan,
                          "c": np.nan
                          }
                          )

    x = data['MilkTotal'].values.tolist()
    t = data['DIM'].values.tolist()

    param_specs = {
        'a': {'value': 30, 'min': 0, 'max': 100},
        'b': {'value': 0.01, 'min': 0.0001, 'max': 0.09},
        'b0': {'value': 0.01, 'min': 0, 'max': 0.09},
        'c': {'value': 0.001, 'min': 0, 'max': 0.005}
        }
    
    dijkstra_fit = fit_model(dijkstra, param_specs, np.array(x), np.array(t))
    a = dijkstra_fit['a']
    b = dijkstra_fit['b']
    b0 = dijkstra_fit['b0']
    c = dijkstra_fit['c']

    t_end = 305
    my_end = dijkstra(t_end, a, b, b0, c)

    return pd.Series({
        "predicted_305_my": my_end,
        "a": a,
        "b": b,
        "b0": b0,
        "c": c
    })


def calculate_persistency(my_end, py, t_end, pt):
    """
    my_end (float): milk yield end of lactation
    py (float): peak milk yield
    t_end (float): days to end of lactation
    pt (float): days to peak milk yield
    """
    return (my_end - py) / (t_end - pt)


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


def get_dijkstra_b_eqn(b):
    return np.exp(b)


def get_dijkstra_b_b0_eqn(b, b0, t):
    return np.exp(b * (1 - np.exp(-b0 * t)) / b0)


def get_dijkstra_b0_eqn(b0, t):
    return np.exp(-b0 * t)


def get_dijkstra_c_eqn(c, t):
    return np.exp(-c * t)

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
