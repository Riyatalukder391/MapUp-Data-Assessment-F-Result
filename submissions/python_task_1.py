from datetime import date

import pandas as pd
from Tools.scripts.dutree import display


def generate_car_matrix(df) -> pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values,
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Pivot the DataFrame to create the desired matrix
    df = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)

    return df


def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Add a new categorical column 'car_type' based on the values of the 'car' column
    df['car_type'] = pd.cut(df['car'],
                                   bins=[float('-inf'), 15, 25, float('inf')],
                                   labels=['low', 'medium', 'high'],
                                   right=False)

    # Calculate the count of occurrences for each 'car_type' category
    type_counts = df['car_type'].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_counts = dict(sorted(type_counts.items()))
    # Write your logic here

    return sorted_type_counts


def get_bus_indexes(df)->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Write your logic here
    bus_mean = df['bus'].mean()

    # Identify indices where the 'bus' values are greater than twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()

    # Sort the indices in ascending order
    sorted_bus_indexes = sorted(bus_indexes)

    return sorted_bus_indexes


def filter_routes(df)->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Write your logic here
    route_avg_truck = df.groupby('route')['truck'].mean()

    # Filter routes where the average of 'truck' column values is greater than 7
    selected_routes = route_avg_truck[route_avg_truck > 7].index.tolist()

    # Sort the list of selected routes
    sorted_routes = sorted(selected_routes)

    return sorted_routes


def multiply_matrix(matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Write your logic here
    modified_dataframe = matrix.copy()

    # Apply the modification logic to each value in the DataFrame
    modified_dataframe = modified_dataframe.map(lambda x: x * 0.75 if x > 20 else x * 1.25)

    # Round the values to 1 decimal place
    matrix = modified_dataframe.round(1)

    return matrix


def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    # Write your logic here
    df['start_timestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'],  format='%A %H:%M:%S')

    # Combine 'endDay' and 'endTime' columns to create an 'end_timestamp' column
    df['end_timestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'],  format='%A %H:%M:%S')
    print(df.to_string())
    # Calculate the difference between start and end timestamps
    time_difference = df['end_timestamp'] - df['start_timestamp']

    # Check if each time period covers a full 24-hour period and spans all 7 days
    completeness_check = (time_difference == pd.Timedelta(days=1) - pd.Timedelta(seconds=1)) & \
                         (df['start_timestamp'].dt.dayofweek == 0) & \
                         (df['end_timestamp'].dt.dayofweek == 6)

    # Create a multi-index boolean series
    completeness_check = completeness_check.groupby(['id', 'id_2']).all()

    return completeness_check
