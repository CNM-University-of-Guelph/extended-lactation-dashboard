"""Feature construction for primiparous cows."""

import numpy as np
import pandas as pd
import scipy

from .feature_construction_helpers import transform_10d_averages, cyclic_encode

pd.options.mode.chained_assignment = None

def primi_feature_construction(current_lactation):
    #10d milk bins
    features = transform_10d_averages(current_lactation, 60)
    features = features.drop(columns=["Parity"])

    # Cyclic encode month
    min_dim = current_lactation.loc[current_lactation.groupby(["Cow"])["DIM"].idxmin()]
    min_dim["Month"] = min_dim["Date"].dt.month
    min_dim = min_dim[["Cow", "Month"]]
    min_dim = cyclic_encode(min_dim, "Month", 12)
    features = features.merge(min_dim, on=["Cow"], how="left")

    # Fit Dijkstra
    results = {}
    grouped = current_lactation.groupby("Cow")

    starting_values = [20, 0.01, 0.01, 0.01]
    lower_bounds = [0.01, 0.0001, 0.0001, 0.0001]
    upper_bounds = [100, 0.1, 0.1, 0.05]
    bounds = (lower_bounds, upper_bounds)

    for name, group in grouped:
        group_filtered = group[group["DIM"] <= 60]
        t = group_filtered["DIM"].values
        y = group_filtered["MilkTotal"].values

        try:
            params, covariance = scipy.optimize.curve_fit(
                dijkstra, t, y, p0=starting_values, bounds=bounds, maxfev=10000
            )
            results[name] = {
                "a": params[0],"b": params[1],"b0": params[2],"c": params[3]
            }
            
        except RuntimeError as e:
            results[name] = {
                "a": np.nan,"b": np.nan,"b0": np.nan,"c": np.nan
            }
        
    dijkstra_results = pd.DataFrame(results).T.reset_index().rename(columns={"index": "Cow"})
    features = features.merge(dijkstra_results, on="Cow", how="left")

    # Predict d305 MY 
    features["predicted_305_my"] = dijkstra(
        305, features["a"], features["b"], features["b0"], features["c"]
        )
    features = features.dropna()

    if features.empty:
        return features

    # TODO Save the scaler for the dataset and load here. MinMax scaling a single 
    # row makes all values 0.
    # MinMax Scaling
    features = features.drop(columns={"Cow"})
    # month_cos = features.pop("Month_cos")
    # month_sin = features.pop("Month_sin")

    # scaler = sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))
    # scaled_data = scaler.fit_transform(features)
    # scaled_dataset = pd.DataFrame(scaled_data, columns=features.columns)
    # scaled_dataset["Month_sin"] = month_sin.values
    # scaled_dataset["Month_cos"] = month_cos.values
    # return scaled_dataset
    return features


def dijkstra(t, a, b, b0, c):
    return a * np.exp((b * (1 - np.exp(-b0 * t)) / b0) - c * t)
