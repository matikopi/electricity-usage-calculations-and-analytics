import pandas as pd
import json

PRICE_VALUE_COLUMN= "value"
NOGA_RATE_COLUMN = "noga_rate_nis_to_kwh"
DATE_COLUMN = "date"

def get_noga_rate_to_merge_with_user_usage(path: str, date_column: str = "date", noga_rate_column: str = NOGA_RATE_COLUMN) -> pd.DataFrame:
    with open(path, 'r') as file:
        data = json.load(file)

    # Convert the JSON into a DataFrame
    rows = []
    for day_date in data:
        date = day_date["date"]
        for entry in day_date["smpData"]:
            entry["date"] = date  # Add the date as a column
            rows.append(entry)

    # Create the DataFrame
    noga_rate = pd.DataFrame(rows)
    noga_rate[date_column] = pd.to_datetime(noga_rate["date"] + ' ' + noga_rate["time"], dayfirst=True)

    noga_rate[date_column] = pd.to_datetime(noga_rate[date_column]).dt.tz_localize('UTC+03:00')
    noga_rate = noga_rate.sort_values(by=date_column, ascending=True)
    noga_rate[NOGA_RATE_COLUMN] = noga_rate["day_Ahead_Constrained_Smp"]
    noga_rate = noga_rate[[date_column, NOGA_RATE_COLUMN,]]

    # Set the 'date' column as the DataFrame index
    noga_rate.set_index(date_column, inplace=True)

    # Create a new date range with 15-minute intervals
    new_index = pd.date_range(start=noga_rate.index.min(), end=noga_rate.index.max(), freq="15T")

    # Reindex the DataFrame to the new date range
    noga_rate_15min = noga_rate.reindex(new_index)

    # Forward-fill the 'rate' column so that the new 15-minute rows have the value of the previous 30-minute row
    noga_rate_15min[noga_rate_column] = noga_rate_15min[noga_rate_column].ffill()

    # Reset the index if you want to keep 'date' as a column
    noga_rate_15min.reset_index(inplace=True)
    return noga_rate_15min.rename(columns={"index": date_column})

def merge_user_usage_with_noga_price(user_usage: pd.DataFrame, noga_rate: pd.DataFrame) -> pd.DataFrame:
    date_column = "date"
    if date_column not in user_usage:
        raise ValueError(f"{date_column} not in user_usage. Can't preform the merge.")
    if date_column not in noga_rate:
        raise ValueError(f"{date_column} not in noga_rate. Can't preform the merge.")
    return user_usage.merge(noga_rate, on="date")


def add_seven_percent_off_noga_rate_price(df: pd.DataFrame, price_value_column: str = PRICE_VALUE_COLUMN, noga_rate_column: str = NOGA_RATE_COLUMN):
    new_pricing_column_name = "7_off_noga_rate"
    if new_pricing_column_name in df:
        raise ValueError(f"{new_pricing_column_name} column already exists in dataframe.")
    df[new_pricing_column_name] = df[price_value_column] * 0.93 * df[noga_rate_column]
    return df


def add_iec_price(df: pd.DataFrame, price_value_column: str = PRICE_VALUE_COLUMN):
    new_pricing_column_name = "iec_plan_price"
    if new_pricing_column_name in df:
        raise ValueError(f"{new_pricing_column_name} column already exists in dataframe.")
    df[new_pricing_column_name] = df[price_value_column] * 0.62
    return df

def add_twenty_percent_off_noga_rate_price(df: pd.DataFrame, price_value_column: str = PRICE_VALUE_COLUMN, noga_rate_column: str = NOGA_RATE_COLUMN, date_column: str = DATE_COLUMN):
    new_pricing_column_name = "20_off_noga_rate"
    if new_pricing_column_name in df:
        raise ValueError(f"{new_pricing_column_name} column already exists in dataframe.")

    df[new_pricing_column_name] = (df[price_value_column] * df[noga_rate_column])
    df.loc[((df[date_column].dt.hour >= 23) | (df[date_column].dt.hour < 7)), new_pricing_column_name] = df.loc[(
            (df[date_column].dt.hour >= 23) | (df[date_column].dt.hour < 7)), price_value_column] * 0.8 * df[noga_rate_column]
    return df

def add_fifteen_percent_off_noga_rate_price(df: pd.DataFrame, price_value_column: str = PRICE_VALUE_COLUMN, noga_rate_column: str = NOGA_RATE_COLUMN, date_column: str = DATE_COLUMN):
    new_pricing_column_name = "15_off_noga_rate"
    if new_pricing_column_name in df:
        raise ValueError(f"{new_pricing_column_name} column already exists in dataframe.")

    df[new_pricing_column_name] = (df[price_value_column] * df[noga_rate_column])
    df.loc[
        (df[date_column].dt.day_of_week != 6)
        & (df[date_column].dt.day_of_week != 7)
        & (df[date_column].dt.hour >= 7)
        & (df[date_column].dt.hour < 17)
        , new_pricing_column_name] = df.loc[
                                    (df[date_column].dt.day_of_week != 6)
                                    & (df[date_column].dt.day_of_week != 7)
                                    & (df[date_column].dt.hour >= 7)
                                    & (df[date_column].dt.hour < 17)
                                    , price_value_column] * 0.85 * df[noga_rate_column]
    return df

def add_eighteen_percent_off_noga_rate_price(df: pd.DataFrame, price_value_column: str = PRICE_VALUE_COLUMN, noga_rate_column: str = NOGA_RATE_COLUMN, date_column: str = DATE_COLUMN):
    new_pricing_column_name = "18_off_noga_rate"
    if new_pricing_column_name in df:
        raise ValueError(f"{new_pricing_column_name} column already exists in dataframe.")

    df[new_pricing_column_name] = (df[price_value_column] * df[noga_rate_column])
    df.loc[((df[date_column].dt.hour >= 14) & (df[date_column].dt.hour < 22)), new_pricing_column_name] = df.loc[(
                (df[date_column].dt.hour >= 14) & (df[date_column].dt.hour < 22)), price_value_column] * 0.82 * df[
                                                                                               noga_rate_column]
    return df