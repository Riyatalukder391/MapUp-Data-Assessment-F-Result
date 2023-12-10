import datetime

import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here

    # Create a DataFrame to store the distance matrix
    unique_locations = sorted(set(df['id_start']) | set(df['id_end']))
    distance_matrix = pd.DataFrame(index=unique_locations, columns=unique_locations)

    # Initialize the matrix with zeros
    distance_matrix = distance_matrix.fillna(0)

    # Populate the matrix with cumulative distances
    for index, row in df.iterrows():
        start, end, distance = row['id_start'], row['id_end'], row['distance']
        distance_matrix.loc[start, end] += distance
        distance_matrix.loc[end, start] += distance  # Accounting for bidirectional distances
    df = distance_matrix.copy()
    return df



def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    distance_matrix = df.reset_index().rename(columns={'index': 'id_start'})

    # Melt the DataFrame to unroll it
    unrolled_df = pd.melt(distance_matrix, id_vars='id_start', var_name='id_end', value_name='distance')

    # Exclude rows where 'id_start' is equal to 'id_end'
    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    # Reset the index
    unrolled_df = unrolled_df.reset_index(drop=True)

    df = unrolled_df.copy()
    return df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    reference_rows = df[df['id_start'] == reference_id]

    # Calculate the average distance for the reference value
    reference_avg_distance = reference_rows['distance'].mean()

    # Calculate the lower and upper thresholds within 10%
    lower_threshold = reference_avg_distance * 0.9
    upper_threshold = reference_avg_distance * 1.1

    # Filter rows where the distance is within the 10% threshold
    within_threshold_rows = df[
        (df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]

    # Get unique values from the 'id_start' column and sort them
    result_ids = sorted(within_threshold_rows['id_start'].unique())

    df= result_ids.copy()

    return df


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Add columns for toll rates based on vehicle types
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df




def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    time_ranges_weekday = [(datetime.time(0, 0, 0), datetime.time(10, 0, 0)),
                           (datetime.time(10, 0, 0), datetime.time(18, 0, 0)),
                           (datetime.time(18, 0, 0), datetime.time(23, 59, 59))]

    time_ranges_weekend = [(datetime.time(0, 0, 0), datetime.time(23, 59, 59))]

    discount_factors_weekday = [0.8, 1.2, 0.8]
    discount_factor_weekend = 0.7

    # Convert columns to datetime types
    print(df)
    df['id_start'] = pd.to_datetime(df['id_start'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # Add columns for start_day, start_time, end_day, and end_time
    df['start_day'] = df['start_time'].dt.day_name()
    df['end_day'] = df['end_time'].dt.day_name()

    # Calculate toll rates based on time intervals
    for i, (start, end) in enumerate(time_ranges_weekday):
        mask = ((df['start_time'].dt.time >= start) & (df['start_time'].dt.time <= end))
        mask |= ((df['end_time'].dt.time >= start) & (df['end_time'].dt.time <= end))
        mask &= (df['start_time'].dt.weekday < 5)  # Weekday condition

        column_name = 'toll_rate_' + str(i)
        df[column_name] = df['distance'] * discount_factors_weekday[i]
        df[column_name] = df[column_name].where(mask, df['distance'])

    # Calculate toll rates for weekends
    mask = (df['start_time'].dt.weekday >= 5)  # Weekend condition
    for i, (start, end) in enumerate(time_ranges_weekend):
        column_name = 'toll_rate_weekend'
        df[column_name] = df['distance'] * discount_factor_weekend
        df[column_name] = df[column_name].where(mask, df['distance'])

    return df
