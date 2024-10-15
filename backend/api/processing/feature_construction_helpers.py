import numpy as np
import pandas as pd

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

